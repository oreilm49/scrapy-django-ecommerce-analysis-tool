from typing import List

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from cms.models import AttributeType
from cms.utils import serialized_values_for_attribute_type, is_value_numeric
from dashboard.models import CategoryTable


class CategoryTableForm(forms.ModelForm):
    """
    Form to filter products by attributes, and build dataset for use in category table.
    """
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
