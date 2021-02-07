from typing import Generator, Any

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from cms import constants
from cms.models import Product, Category, ProductQuerySet


class ProductMergeForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.published())
    duplicates = forms.ModelMultipleChoiceField(queryset=Product.objects.published())

    def clean_duplicates(self):
        duplicates = self.cleaned_data['duplicates']
        product = self.cleaned_data['product']
        if duplicates.filter(pk=product.pk):
            raise ValidationError(_('{product} cannot be a duplicate of itself').format(product=product))
        return self.cleaned_data['duplicates']

    @transaction.atomic
    def save(self) -> Product:
        for duplicate in self.cleaned_data['duplicates']:
            self.merge_product(self.cleaned_data['product'], duplicate)
        return self.cleaned_data['product']

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

    class Media:
        js = 'js/select2.min.js', 'js/duplicates.js',
        css = {
            'all': (
                'css/select2.min.css',
            ),
        }


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


