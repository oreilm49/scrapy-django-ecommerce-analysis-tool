from django.contrib import admin
from django.urls import path

from cms.models import Website, Url, Category, Selector, Unit, Product, ProductAttribute, WebsiteProductAttribute, \
    ProductImage, AttributeType, CategoryAttributeConfig
from cms.views.admin import ProductMapView, AttributeTypeMapView


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


class CategoryAttributeConfigInlineAdmin(admin.TabularInline):
    model = CategoryAttributeConfig
    extra = 0
    fields = 'order', 'attribute_type', 'weight', 'publish',
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'parent', 'alternate_names',
    list_filter = 'parent',
    inlines = CategoryAttributeConfigInlineAdmin,


@admin.register(Selector)
class SelectorAdmin(admin.ModelAdmin):
    list_display = 'id', 'selector_type', 'css_selector', 'website', 'regex', 'parent',
    list_editable = 'css_selector', 'regex', 'parent',
    list_filter = 'website',


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'alternate_names', 'widget', 'repeat',


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'id', 'model', 'category', 'alternate_models',
    list_filter = 'category',
    list_per_page = 25


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = 'id', 'attribute_type', 'data', 'product',
    list_editable = 'data',
    list_filter = 'product', 'product__category', 'attribute_type',


@admin.register(WebsiteProductAttribute)
class WebsiteProductAttributeAdmin(admin.ModelAdmin):
    list_display = 'id', 'website', 'attribute_type', 'data', 'product',
    list_editable = 'data',
    list_filter = 'website', 'product', 'product__category', 'attribute_type',


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = 'id', 'product', 'image_type', 'image',
    list_filter = 'image_type', 'product',


@admin.register(AttributeType)
class AttributeTypeAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'alternate_names', 'unit',
    list_filter = 'name', 'alternate_names', 'unit',


def get_admin_urls(urls):
    def get_urls():
        return urls + [
            path('map_products/', admin.site.admin_view(ProductMapView.as_view()), name="map_products"),
            path('map_attribute_types/', admin.site.admin_view(AttributeTypeMapView.as_view()), name="map_attribute_types"),
        ]
    return get_urls


admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
