from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from cms import constants
from cms.models import Product, Category, ProductQuerySet, BaseModel, AttributeType


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
    target = forms.ModelChoiceField(queryset=Product.objects.published())
    duplicates = forms.ModelMultipleChoiceField(queryset=Product.objects.published())

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
    target = forms.ModelChoiceField(queryset=AttributeType.objects.published())
    duplicates = forms.ModelMultipleChoiceField(queryset=AttributeType.objects.published())

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


