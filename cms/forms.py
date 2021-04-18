from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import modelformset_factory
from django.utils.translation import gettext as _
from pint import Quantity

from cms import constants
from cms.data_processing.units import UnitManager
from cms.models import Product, Category, ProductQuerySet, BaseModel, AttributeType, ProductAttribute, Unit


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
        if attribute_type.unit:
            duplicate: AttributeType = duplicate.convert_unit(attribute_type.unit)
        elif duplicate.unit:
            attribute_type: AttributeType = attribute_type.convert_unit(duplicate.unit)
        attribute_type_products = attribute_type.productattributes.values_list('product', flat=True)
        duplicate.productattributes.exclude(product__in=attribute_type_products).update(attribute_type=attribute_type)
        duplicate.productattributes.all().delete()
        duplicate.websiteproductattributes.update(attribute_type=attribute_type)
        attribute_type.alternate_names.append(duplicate.name)
        attribute_type.alternate_names += duplicate.alternate_names
        attribute_type.save()
        duplicate.delete()
        attribute_type.productattributes.serialize()
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


class ProductAttributeForm(forms.ModelForm):
    data = forms.CharField(label=_('Data'), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.fields.get('product'):
            self.fields['product'].disabled = True
        if self.instance.attribute_type:
            self.fields['attribute_type'].disabled = True
        if self.initial.get('attribute_type'):
            if self.attribute_type.unit:
                self.fields['data'] = self.attribute_type.unit.field_class(label=_('Data'), required=True)
        if self.initial.get('data'):
            self.initial['data'] = self.initial['data']['value']

    class Meta:
        model = ProductAttribute
        fields = 'product', 'attribute_type', 'data'

    def clean_data(self):
        value = self.cleaned_data['data']
        attribute_type: AttributeType = self.cleaned_data['attribute_type']
        if attribute_type.unit:
            try:
                value = attribute_type.unit.serializer.serializer(value)
            except Exception as e:
                raise ValidationError(_("Unable to serialize data. Please ensure you're using the correct data type for this attribute: '{error}'").format(error=e))
        return {'value': value}

    @property
    def attribute_type(self) -> AttributeType:
        attribute_type = self.initial['attribute_type']
        if isinstance(attribute_type, AttributeType):
            return attribute_type
        else:
            return AttributeType.objects.get(pk=self.initial['attribute_type'])


def get_product_attribute_formset(extra: int):
    return modelformset_factory(ProductAttribute, form=ProductAttributeForm, extra=extra)


class AttributeTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_unit = self.instance.unit

    class Meta:
        model = AttributeType
        fields = 'name', 'alternate_names', 'unit'

    def clean_unit(self):
        unit: Unit = self.cleaned_data['unit']
        if unit and self.instance.unit:
            try:
                units: UnitManager = UnitManager()
                quantity: Quantity = units.ureg(f"2{self.instance.unit}")
                quantity.to(unit.name)
                return unit
            except Exception as e:
                raise ValidationError(str(e))

    @transaction.atomic
    def save(self, commit=True):
        """If unit has changed, serialize and convert all product attribute values"""
        if 'unit' in self.changed_data:
            self.instance.convert_product_attributes(self.cleaned_data['unit'], from_unit=self.initial_unit)
        return super().save(commit)


