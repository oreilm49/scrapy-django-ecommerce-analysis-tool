from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView

from cms.forms import ProductMergeForm, AttributeTypeMergeForm


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
