from typing import List

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.postgres.forms import SimpleArrayField
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from cms import constants
from cms.models import Product, Category, ProductQuerySet, BaseModel, AttributeType
from cms.utils import serialized_values_for_attribute_type, is_value_numeric


class BaseMergeForm(forms.Form):

    def clean_duplicates(self):
        duplicates = self.cleaned_data['duplicates']
        target = self.cleaned_data['target']
        if duplicates.filter(pk=target.pk):
            raise ValidationError(_('{target} cannot be a duplicate of itself').format(target=target))
        return self.cleaned_data['duplicates']

    @transaction.atomic
    def save(self) -> Product:
        for duplicate in self.cleaned_data['duplicates']:
            self.merge(self.cleaned_data['target'], duplicate)
        return self.cleaned_data['target']

    def merge(self, target: BaseModel, duplicate: BaseModel):
        return

    class Media:
        js = 'js/select2.min.js', 'js/duplicates.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }


class ProductMergeForm(BaseMergeForm):
    target = forms.ModelChoiceField(queryset=Product.objects.published(), label=_('Product'))
    duplicates = forms.ModelMultipleChoiceField(queryset=Product.objects.published(), label=_('Duplicates'), help_text=_('All relational data from duplicates will be merged into product.'))

    def merge(self, product: Product, duplicate: Product) -> Product:
        """
        Merges all attributes of duplicate into product, then deletes duplicate.
        :param product: the source product.
        :param duplicate: the product to be merged into source.
        :return: the merged product instance.
        """
        missing_attributes = duplicate.productattributes.exclude(attribute_type__in=product.productattributes.values_list('attribute_type'))
        missing_attributes.update(product=product)
        product.alternate_models.append(duplicate.model)
        product.save()
        if product.image_main_required:
            duplicate.images.filter(image_type=constants.MAIN).update(product=product)
        if product.image_thumb_required:
            duplicate.images.filter(image_type=constants.THUMBNAIL).update(product=product)
        duplicate.websiteproductattributes.update(product=product)
        duplicate.delete()
        return product


class AttributeTypeMergeForm(BaseMergeForm):
    target = forms.ModelChoiceField(queryset=AttributeType.objects.published(), label=_('Attribute Type'))
    duplicates = forms.ModelMultipleChoiceField(queryset=AttributeType.objects.published(), label=_('Duplicates'), help_text=_('All relational data from duplicates will be merged into the selected attribute type.'))

    def merge(self, attribute_type: AttributeType, duplicate: AttributeType) -> AttributeType:
        """
        Merges all relations of duplicate into attribute type, then deletes duplicate.
        :param attribute_type: the source attribute type.
        :param duplicate: the attribute type to be merged into source.
        :return: the merged attribute type instance.
        """
        attribute_type_products = attribute_type.productattributes.values_list('product', flat=True)
        duplicate.productattributes.exclude(product__in=attribute_type_products).update(attribute_type=attribute_type)
        duplicate.productattributes.all().delete()
        duplicate.websiteproductattributes.update(attribute_type=attribute_type)
        if not attribute_type.unit and duplicate.unit:
            attribute_type.unit = duplicate.unit
        attribute_type.alternate_names.append(duplicate.name)
        attribute_type.alternate_names += duplicate.alternate_names
        attribute_type.save()
        duplicate.delete()
        return attribute_type


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.published(), label=_('Category'), required=False)
    q = forms.CharField(label=_('Search'), required=False)

    def search(self, queryset: ProductQuerySet) -> ProductQuerySet:
        if self.is_valid():
            if self.cleaned_data['category']:
                queryset = queryset.filter(category=self.cleaned_data['category'])
            if self.cleaned_data['q']:
                queryset = queryset.filter(model__contains=self.cleaned_data['q'])
            return queryset
        return queryset

    class Media:
        css = {
            'all': (
                'css/form-inline.css',
            ),
        }


class CategoryTableForm(forms.Form):
    """
    Form to filter products by attributes, and build dataset for use in category table.
    """
    x_axis_attribute = forms.ModelChoiceField(AttributeType.objects.published(), label=_('X Axis Attribute'), help_text=_('The attribute used to group products into rows on the table.'))
    x_axis_values = SimpleArrayField(forms.CharField(max_length=100), label=_('X Axis Values'), help_text=_('The values products must have for the x axis attribute in order to appear in the table.'))
    y_axis_attribute = forms.ModelChoiceField(AttributeType.objects.published(), label=_('Y Axis Attribute'), help_text=_('The attribute used to group products into rows on the table.'))
    y_axis_values = SimpleArrayField(forms.CharField(max_length=100), label=_('X Axis Values'), help_text=_('The values products must have for the y axis attribute in order to appear in the table.'))
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
