from django.contrib import admin
from django.urls import path

from cms.forms import ProductAttributeForm, AttributeTypeForm
from cms.models import Website, Url, Category, Selector, Unit, Product, ProductAttribute, WebsiteProductAttribute, \
    ProductImage, AttributeType, CategoryAttributeConfig, SpiderResult, EprelCategory
from cms.views.admin import ProductMapView, AttributeTypeMapView, ProductAttributeBulkCreateView


class SelectorInlineAdmin(admin.TabularInline):
    model = Selector
    extra = 0
    fields = 'selector_type', 'css_selector', 'regex', 'parent',
    show_change_link = True


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'domain'
    list_editable = 'name', 'domain'
    inlines = SelectorInlineAdmin,


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = 'id', 'website', 'category', 'url', 'url_type', 'last_scanned'
    list_editable = 'website', 'category', 'url', 'url_type'
    list_filter = 'website', 'category', 'url_type'
    exclude = 'last_scanned',


class CategoryAttributeConfigInlineAdmin(admin.TabularInline):
    model = CategoryAttributeConfig
    extra = 0
    fields = 'order', 'attribute_type', 'weight', 'scoring', 'publish',
    show_change_link = True


class EprelCategoryInlineAdmin(admin.TabularInline):
    model = EprelCategory
    extra = 0
    fields = 'name',
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'parent', 'alternate_names',
    list_filter = 'parent',
    inlines = CategoryAttributeConfigInlineAdmin, EprelCategoryInlineAdmin,


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'alternate_names', 'widget', 'repeat',


class ProductAttributeInlineAdmin(admin.TabularInline):
    model = ProductAttribute
    extra = 0
    fields = 'attribute_type', 'data',
    show_change_link = True
    classes = ['collapse']
    form = ProductAttributeForm


class ProductImageInlineAdmin(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = 'image_type', 'image',
    show_change_link = True
    classes = ['collapse']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'id', 'model', 'category', 'alternate_models',
    list_filter = 'category',
    list_per_page = 25
    inlines = ProductAttributeInlineAdmin, ProductImageInlineAdmin,


@admin.register(WebsiteProductAttribute)
class WebsiteProductAttributeAdmin(admin.ModelAdmin):
    list_display = 'id', 'website', 'attribute_type', 'data', 'product',
    list_editable = 'data',
    list_filter = 'website', 'product', 'product__category', 'attribute_type',


@admin.register(AttributeType)
class AttributeTypeAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'alternate_names', 'unit',
    list_filter = 'name', 'alternate_names', 'unit',
    inlines = ProductAttributeInlineAdmin,
    form = AttributeTypeForm


@admin.register(SpiderResult)
class SpiderResultAdmin(admin.ModelAdmin):
    list_display = 'created', 'spider_name', 'website', 'category', 'items_scraped',


def get_admin_urls(urls):
    def get_urls():
        return urls + [
            path('map_products/', admin.site.admin_view(ProductMapView.as_view()), name="map_products"),
            path('map_attribute_types/', admin.site.admin_view(AttributeTypeMapView.as_view()), name="map_attribute_types"),
            path('map_product_attributes/', admin.site.admin_view(ProductAttributeBulkCreateView.as_view()), name="map_product_attributes"),
        ]
    return get_urls


admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
