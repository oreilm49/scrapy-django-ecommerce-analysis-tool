from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from cms import constants
from cms.models import Product


class ProductMergeForm(forms.Form):
    duplicates = forms.ModelMultipleChoiceField(queryset=Product.objects.none(), label=_('Select Duplicates'))

    def __init__(self, *args, product: Product = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        self.fields['duplicates'].queryset = Product.objects.published().exclude(pk=product.pk)

    def clean_duplicates(self):
        duplicates = self.cleaned_data['duplicates']
        if duplicates.filter(pk=self.product.pk):
            raise ValidationError({'duplicates': _('{product} cannot be a duplicate of itself').format(product=self.product)})
        return duplicates

    @transaction.atomic
    def save(self) -> Product:
        for duplicate in self.cleaned_data['duplicates']:
            self.merge_product(self.product, duplicate)
        return self.product

    def merge_product(self, product: Product, duplicate: Product) -> Product:
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
