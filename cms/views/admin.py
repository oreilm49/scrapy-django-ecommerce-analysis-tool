from typing import List, Dict

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView

from cms.forms import ProductMergeForm, AttributeTypeMergeForm, ProductAttributeFormSet
from cms.models import CategoryAttributeConfig, Product, ProductAttribute


class MapViewMixin(SuccessMessageMixin, FormView):
    template_name = 'site/simple_form.html'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        return super(MapViewMixin, self).form_invalid(form)


class ProductMapView(MapViewMixin):
    success_message = _('Products mapped successfully')
    form_class = ProductMergeForm

    def get_success_url(self):
        return reverse('admin:map_products')


class AttributeTypeMapView(MapViewMixin):
    template_name = 'site/simple_form.html'
    success_message = _('Attribute types mapped successfully')
    form_class = AttributeTypeMergeForm

    def get_success_url(self):
        return reverse('admin:map_attribute_types')


class ProductAttributeBulkCreateView(SuccessMessageMixin, FormView):
    template_name = 'site/simple_formset.html'
    success_message = _('Products attributes updated successfully')
    form_class = ProductAttributeFormSet

    def get_success_url(self):
        return reverse('admin:map_product_attributes')

    def get_form(self, form_class=None):
        return ProductAttributeFormSet(self.request.POST or None, initial=self.get_initial_data(), queryset=ProductAttribute.objects.none())

    def get_initial_data(self):
        """
        Gets list of dicts for each product attribute required.
        CategoryAttributeConfig is used to identify attributes required.
        """
        output_data: List[Dict[str, str, str]] = []
        configs: QuerySet[CategoryAttributeConfig] = CategoryAttributeConfig.objects.published().order_by('category__name')
        for config in configs.iterator():
            output_data += [{'product': product, 'attribute_type': config.attribute_type} for product in
                            Product.objects.published().exclude(productattributes__attribute_type=config.attribute_type)]
        return output_data

    def get_context_data(self, **kwargs):
        return super().get_context_data(formset=self.get_form(), **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        formset = self.get_form()
        if not formset.is_valid():
            messages.error(request, _('There was an error processing product attributes'))
            return render(request, self.template_name, {'formset': formset})
        formset.save()
        return self.form_valid(formset)
