from typing import List

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _

from cms.models import AttributeType, Category, ProductQuerySet
from cms.utils import serialized_values_for_attribute_type, is_value_numeric
from dashboard.models import CategoryTable, CategoryTableQuerySet
from dashboard.utils import get_brands


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
        js = 'js/select2.min.js', 'js/duplicates.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }


class ProductsFilterForm(forms.Form):
    q = forms.CharField(label=_('Search'), required=False)
    category = forms.ModelChoiceField(label=_('Category'), queryset=Category.objects.published(), required=False)
    price_low = forms.FloatField(label=_('Price: low'), required=False)
    price_high = forms.FloatField(label=_('Price: high'), required=False)
    brands = forms.MultipleChoiceField(label=_('Brands'), choices=((brand, brand) for brand in get_brands()), required=False)

    def search(self, queryset: ProductQuerySet) -> ProductQuerySet:
        if self.cleaned_data.get('q'):
            queryset = queryset.filter(Q(model__contains=self.cleaned_data['q']) |
                                       Q(alternate_models__contains=[self.cleaned_data['q']]) |
                                       Q(category__name__contains=[self.cleaned_data['q']]))
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
        js = 'js/select2.min.js', 'js/duplicates.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }
