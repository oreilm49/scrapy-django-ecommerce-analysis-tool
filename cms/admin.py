from django.contrib import admin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.urls import path, reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView

from cms.forms import ProductMergeForm
from cms.models import Website, Url, Category, Selector, Unit, Product, ProductAttribute, WebsiteProductAttribute, \
    ProductImage, AttributeType


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'domain'
    list_editable = 'name', 'domain'


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = 'id', 'website', 'category', 'url', 'url_type', 'last_scanned'
    list_editable = 'website', 'category', 'url', 'url_type'
    list_filter = 'website', 'category', 'url_type'
    exclude = 'last_scanned',


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'parent', 'alternate_names',
    list_editable = 'name', 'parent', 'alternate_names',
    list_filter = 'parent',


@admin.register(Selector)
class SelectorAdmin(admin.ModelAdmin):
    list_display = 'id', 'selector_type', 'css_selector', 'website', 'regex', 'parent',
    list_editable = 'selector_type', 'css_selector', 'website', 'regex', 'parent',
    list_filter = 'selector_type', 'website', 'parent',


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'alternate_names', 'data_type', 'repeat',
    list_editable = 'name', 'alternate_names', 'data_type', 'repeat',


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'id', 'model', 'category', 'alternate_models',
    list_editable = 'model', 'category', 'alternate_models',
    list_filter = 'category',
    list_per_page = 50


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = 'id', 'attribute_type', 'value', 'product',
    list_editable = 'attribute_type', 'value', 'product',
    list_filter = 'product', 'product__category', 'attribute_type',


@admin.register(WebsiteProductAttribute)
class WebsiteProductAttributeAdmin(admin.ModelAdmin):
    list_display = 'id', 'website', 'attribute_type', 'value', 'product',
    list_editable = 'website', 'attribute_type', 'value', 'product',
    list_filter = 'website', 'product', 'product__category', 'attribute_type',


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = 'id', 'product', 'image_type', 'image',
    list_filter = 'image_type', 'product',


@admin.register(AttributeType)
class AttributeTypeAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'alternate_names', 'unit',
    list_filter = 'name', 'alternate_names', 'unit',


class ProductMapView(SuccessMessageMixin, FormView):
    template_name = 'site/map_products.html'
    success_message = _('Products mapped successfully')
    form_class = ProductMergeForm

    def get_success_url(self):
        return reverse('admin:map_products')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form: ProductMergeForm = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        return super(ProductMapView, self).form_invalid(form)


def get_admin_urls(urls):
    def get_urls():
        return urls + [
            path('map_products/', admin.site.admin_view(ProductMapView.as_view()), name="map_products"),
        ]
    return get_urls


admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
