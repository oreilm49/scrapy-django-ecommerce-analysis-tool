from django.contrib import admin

from cms.models import Website, Url, Category, Selector, Unit, PageDataItem, Product, ProductAttribute


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
    list_display = 'id', 'name',
    list_editable = 'name',


@admin.register(PageDataItem)
class PageDataItemAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'data_type', 'alternate_names', 'website', 'selector', 'unit', 'repeat',
    list_editable = 'name', 'data_type', 'alternate_names', 'website', 'selector', 'unit', 'repeat',
    list_filter = 'data_type', 'website', 'unit',


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'id', 'model', 'category', 'alternate_models',
    list_editable = 'model', 'category', 'alternate_models',
    list_filter = 'category',


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = 'id', 'data_type', 'value', 'product',
    list_editable = 'data_type', 'value', 'product',
    list_filter = 'product', 'product__category', 'data_type',
