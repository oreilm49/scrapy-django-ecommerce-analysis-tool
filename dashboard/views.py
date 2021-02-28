import itertools
from collections import namedtuple
from typing import Iterator, Tuple

from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView

from dashboard.forms import CategoryTableForm
from cms.models import Product
from cms.utils import products_grouper
from dashboard.models import CategoryTable
from dashboard.toolbar import ToolbarItem

CategoryTableProduct = namedtuple('CategoryTableProduct', ['x_axis_grouper', 'y_axis_grouper', 'product'])


class CategoryTableMixin:

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(
            toolbar_items=[ToolbarItem(
                label='Create',
                url=reverse('category-table-create'),
                icon='fa fa-plus'
            )]
        )
        return data


class CategoryTables(CategoryTableMixin, ListView):
    template_name = 'views/category_tables.html'
    queryset = CategoryTable.objects.published()


class CategoryTableCreate(CategoryTableMixin, CreateView):
    template_name = 'views/category_table_modify.html'
    queryset = CategoryTable.objects.published()
    form_class = CategoryTableForm


class CategoryTableDetail(CategoryTableMixin, DetailView):
    template_name = 'views/category_table.html'
    queryset = CategoryTable.objects.published()

    @property
    def table(self):
        return self.get_object(self.queryset)

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        products = [CategoryTableProduct(
            x_axis_grouper=products_grouper(product, self.table.x_axis_attribute, self.table.x_axis_values),
            y_axis_grouper=products_grouper(product, self.table.y_axis_attribute, self.table.y_axis_values),
            product=product
        ) for product in self.table.products(Product.objects.published())]
        y_axis_groups: Iterator[Tuple] = itertools.groupby(
            sorted(products, key=lambda product: product.y_axis_grouper),
            key=lambda product: product.y_axis_grouper
        )
        table_data = {}
        for grouper, products in y_axis_groups:
            table_data[grouper] = [product for product in products]
        data.update(
            table_data=table_data,
            x_axis_values=self.table.x_axis_values,
        )
        return data
