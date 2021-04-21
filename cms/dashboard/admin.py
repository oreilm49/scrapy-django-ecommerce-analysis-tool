from django.contrib import admin

from cms.dashboard.models import CategoryTable, CategoryGapAnalysisReport, CategoryTableAttribute


class CategoryTableAttributeInlineAdmin(admin.TabularInline):
    model = CategoryTableAttribute
    extra = 0
    fields = 'attribute',
    show_change_link = True


@admin.register(CategoryTable)
class CategoryTableAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'user', 'category',
    inlines = CategoryTableAttributeInlineAdmin,


@admin.register(CategoryGapAnalysisReport)
class CategoryGapAnalysisReportAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'user', 'category', 'brand',
