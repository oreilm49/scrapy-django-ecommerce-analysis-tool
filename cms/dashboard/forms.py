from typing import List

from bootstrap_daterangepicker.fields import DateRangeField
from bootstrap_daterangepicker.widgets import DateRangeWidget
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils import timezone

from cms.dashboard.models import CategoryTable, CategoryTableQuerySet, CategoryGapAnalysisReport, \
    CategoryGapAnalysisQuerySet
from cms.dashboard.utils import get_brands
from cms.models import AttributeType, Category, ProductQuerySet, Website, WebsiteProductAttributeQuerySet
from cms.utils import serialized_values_for_attribute_type, is_value_numeric


class CategoryTableForm(forms.ModelForm):
    """
    Form to filter products by attributes, and build dataset for use in category table.
    """
    x_axis_values = SimpleArrayField(base_field=forms.CharField())
    y_axis_values = SimpleArrayField(base_field=forms.CharField())

    class Meta:
        model = CategoryTable
        fields = ['name', 'x_axis_attribute', 'x_axis_values', 'y_axis_attribute', 'y_axis_values', 'category', 'query']

    def clean_x_axis_values(self) -> List[str]:
        return self.clean_axis_attributes(self.cleaned_data['x_axis_values'], self.cleaned_data['x_axis_attribute'])

    def clean_y_axis_values(self) -> List[str]:
        return self.clean_axis_attributes(self.cleaned_data['y_axis_values'], self.cleaned_data['y_axis_attribute'])

    def clean_axis_attributes(self, values: List[str], attribute_type: AttributeType):
        """
        Ensures that string values submitted for attribute exist and can be used to filter
        products. If values are numeric, cleaned data is returned. Numeric data can be used for
        value ranges and an attribute doesn't need to exist with that exact value.
        """
        if is_value_numeric(values[0]):
            return serialized_values_for_attribute_type(values, attribute_type)
        for value in values:
            if not attribute_type.productattributes.filter(data__value=value).exists() and not attribute_type.websiteproductattributes.filter(data__value=value).exists():
                raise ValidationError(_("'{attribute}' with value '{value}' does not exist.").format(attribute=attribute_type.name, value=value))
        return serialized_values_for_attribute_type(values, attribute_type)

    class Media:
        js = 'js/category_line_up.js',


class CategoryTableFilterForm(forms.Form):
    q = forms.CharField(label=_('Search'), required=False)
    category = forms.ModelChoiceField(label=_('Category'), empty_label=_('Category'), queryset=Category.objects.published(), required=False)
    attribute_type = forms.ModelMultipleChoiceField(label=_('Specs'), queryset=AttributeType.objects.published(), required=False)

    def search(self, queryset: CategoryTableQuerySet) -> CategoryTableQuerySet:
        if self.cleaned_data.get('q'):
            queryset = queryset.filter(Q(name__contains=self.cleaned_data['q']) |
                                       Q(query__contains=self.cleaned_data['q']) |
                                       Q(x_axis_values__contains=self.cleaned_data['q']) |
                                       Q(y_axis_values__contains=self.cleaned_data['q']) |
                                       Q(x_axis_attribute__name__contains=self.cleaned_data['q']) |
                                       Q(y_axis_attribute__name__contains=self.cleaned_data['q']) |
                                       Q(x_axis_attribute__alternate_names__contains=[self.cleaned_data['q']]) |
                                       Q(y_axis_attribute__alternate_names__contains=[self.cleaned_data['q']]))
        if self.cleaned_data.get('category'):
            queryset = queryset.filter(category=self.cleaned_data['category'])
        if self.cleaned_data.get('attribute_type'):
            queryset = queryset.filter(Q(x_axis_attribute__in=self.cleaned_data['attribute_type']) |
                                       Q(y_axis_attribute__in=self.cleaned_data['attribute_type']))
        return queryset

    class Media:
        js = 'js/select2.min.js', 'js/category_tables_filter.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }


class ProductsFilterForm(forms.Form):
    q = forms.CharField(label=_('Search'), required=False)
    category = forms.ModelChoiceField(label=_('Category'), empty_label=_('Category'), queryset=Category.objects.published(), required=False)
    price_low = forms.FloatField(label=_('Price: low'), required=False)
    price_high = forms.FloatField(label=_('Price: high'), required=False)
    brands = forms.MultipleChoiceField(label=_('Brands'), choices=(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brands'].choices = ((brand, brand) for brand in get_brands())

    def search(self, queryset: ProductQuerySet) -> ProductQuerySet:
        if self.cleaned_data.get('q'):
            queryset = queryset.filter(Q(model__contains=self.cleaned_data['q']) |
                                       Q(alternate_models__contains=[self.cleaned_data['q']]) |
                                       Q(category__name__contains=self.cleaned_data['q']))
        if self.cleaned_data.get('price_low'):
            queryset = queryset.filter(websiteproductattributes__attribute_type__name='price',
                                       websiteproductattributes__data__value__gte=self.cleaned_data['price_low'])
        if self.cleaned_data.get('price_high'):
            queryset = queryset.filter(websiteproductattributes__attribute_type__name='price',
                                       websiteproductattributes__data__value__lte=self.cleaned_data['price_high'])
        if self.cleaned_data.get('brands'):
            queryset = queryset.filter(productattributes__attribute_type__name='brand',
                                       productattributes__data__value__in=self.cleaned_data['brands'])
        return queryset

    class Media:
        js = 'js/select2.min.js', 'js/products_filter.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }


class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.Textarea, label=_('How can we improve?'), help_text=_('Please provide as much context as possible'))


class ProductPriceFilterForm(forms.Form):
    website = forms.ModelChoiceField(label=_('Website'), queryset=Website.objects.published(), required=False)
    price_low = forms.FloatField(label=_('Price: low'), required=False)
    price_high = forms.FloatField(label=_('Price: high'), required=False)
    date_range = DateRangeField(widget=DateRangeWidget(
        picker_options={
            'showDropdowns': True,
            'autoUpdateInput': True,
            'minYear': 2010,
            'maxYear': timezone.now().year + 1,
            'linkedCalendars': False,
        },
        format='%Y-%m-%d',
    ), label=_('Date range'))

    def search(self, queryset: WebsiteProductAttributeQuerySet) -> WebsiteProductAttributeQuerySet:
        if self.cleaned_data.get('website'):
            queryset = queryset.filter(website=self.cleaned_data['website'])
        if self.cleaned_data.get('price_low'):
            queryset = queryset.filter(attribute_type__name='price', data__value__gte=self.cleaned_data['price_low'])
        if self.cleaned_data.get('price_high'):
            queryset = queryset.filter(attribute_type__name='price', data__value__lte=self.cleaned_data['price_high'])
        if self.cleaned_data.get('date_range'):
            start, end = self.cleaned_data['date_range']
            queryset = queryset.filter(created__gte=start, created__lte=end)
        return queryset


class CategoryGapAnalysisForm(forms.ModelForm):
    brand = forms.ChoiceField(label=_('Brand'), choices=(), required=True, help_text=_("The brand you'd like to use as the target for this analysis."))
    price_clusters = SimpleArrayField(base_field=forms.CharField())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].choices = ((brand, brand) for brand in get_brands())
        self.fields['websites'].required = False

    class Meta:
        model = CategoryGapAnalysisReport
        fields = 'name', 'category', 'brand', 'websites', 'price_clusters',

    class Media:
        js = 'js/select2.min.js', 'js/category_gap_analysis_filter.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }


class CategoryGapAnalysisFilterForm(forms.Form):
    q = forms.CharField(label=_('Search'), required=False)
    category = forms.ModelChoiceField(label=_('Category'), empty_label=_('Category'), queryset=Category.objects.published(), required=False)
    websites = forms.ModelMultipleChoiceField(label=_('Websites'), queryset=Website.objects.published(), required=False)

    def search(self, queryset: CategoryGapAnalysisQuerySet) -> CategoryGapAnalysisQuerySet:
        if self.cleaned_data.get('q'):
            queryset = queryset.filter(Q(name__contains=self.cleaned_data['q']) |
                                       Q(brand__contains=self.cleaned_data['q']) |
                                       Q(websites__name__contains=[self.cleaned_data['q']]))
        if self.cleaned_data.get('category'):
            queryset = queryset.filter(category=self.cleaned_data['category'])
        if self.cleaned_data.get('websites'):
            queryset = queryset.filter(Q(websites__in=self.cleaned_data['websites']))
        return queryset

    class Media:
        js = 'js/select2.min.js', 'js/category_gap_analysis_filter.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }
