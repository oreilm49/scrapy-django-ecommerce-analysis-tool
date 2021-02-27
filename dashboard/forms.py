from typing import List

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.postgres.forms import SimpleArrayField
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from cms.models import Category, ProductQuerySet, AttributeType
from cms.utils import serialized_values_for_attribute_type, is_value_numeric


class CategoryTableForm(forms.Form):
    """
    Form to filter products by attributes, and build dataset for use in category table.
    """
    x_axis_attribute = forms.ModelChoiceField(AttributeType.objects.published(), label=_('X Axis Attribute'), help_text=_('The attribute used to group products into rows on the table.'))
    x_axis_values = SimpleArrayField(forms.CharField(max_length=100), label=_('X Axis Values'), help_text=_('The values products must have for the x axis attribute in order to appear in the table.'))
    y_axis_attribute = forms.ModelChoiceField(AttributeType.objects.published(), label=_('Y Axis Attribute'), help_text=_('The attribute used to group products into rows on the table.'))
    y_axis_values = SimpleArrayField(forms.CharField(max_length=100), label=_('Y Axis Values'), help_text=_('The values products must have for the y axis attribute in order to appear in the table.'))
    category = forms.ModelChoiceField(Category.objects.published(), label=_('Category'), help_text=_('The category products should belong to in order to appear in the table.'))
    q = forms.CharField(label=_('Search'), required=False, help_text=_('General search text used to further filter products.'))

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

    def search(self, queryset: ProductQuerySet) -> QuerySet:
        if self.is_valid():
            product_pks: List[int] = []
            if not is_value_numeric(self.cleaned_data['x_axis_values'][0]):
                products_from_attributes: ProductQuerySet = self.cleaned_data['x_axis_attribute'].productattributes.filter(data__value__in=self.cleaned_data['x_axis_values'])
                product_pks.append(products_from_attributes.values_list('product', flat=True))
            if not is_value_numeric(self.cleaned_data['y_axis_values'][0]):
                products_from_attributes: ProductQuerySet = self.cleaned_data['y_axis_attribute'].productattributes.filter(data__value__in=self.cleaned_data['y_axis_values'])
                product_pks.append(products_from_attributes.values_list('product', flat=True))
            if self.cleaned_data['q']:
                queryset = queryset.filter(model__contains=self.cleaned_data['q'])
            return queryset.filter(pk__in=product_pks, category=self.cleaned_data['category'])
        return queryset

    class Media:
        js = 'js/category_line_up.js',
