import itertools
from collections import namedtuple
from typing import Iterator, Tuple

from django.views.generic import ListView, DetailView

from dashboard.forms import CategoryTableForm
from cms.models import Product
from cms.utils import products_grouper
from dashboard.models import CategoryTable

CategoryTableProduct = namedtuple('CategoryTableProduct', ['x_axis_grouper', 'y_axis_grouper', 'product'])


class CategoryTables(ListView):
    template_name = 'views/category_tables.html'
    queryset = CategoryTable.objects.published()


class CategoryTableDetail(DetailView):
    template_name = 'views/category_table.html'

    def get_form(self):
        return CategoryTableForm(self.request.GET or None)

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        form: CategoryTableForm = self.get_form()
        data.update(form=self.get_form())
        if self.request.GET:
            if form.is_valid():
                products = [CategoryTableProduct(
                    x_axis_grouper=products_grouper(product, form.cleaned_data['x_axis_attribute'], form.cleaned_data['x_axis_values']),
                    y_axis_grouper=products_grouper(product, form.cleaned_data['y_axis_attribute'], form.cleaned_data['y_axis_values']),
                    product=product
                ) for product in form.search(Product.objects.published()).iterator()]
                y_axis_groups: Iterator[Tuple] = itertools.groupby(
                    sorted(products, key=lambda product: product.y_axis_grouper),
                    key=lambda product: product.y_axis_grouper
                )
                table_data = {}
                for grouper, products in y_axis_groups:
                    table_data[grouper] = [product for product in products]
                data.update(
                    table_data=table_data,
                    x_axis_values=form.cleaned_data['x_axis_values'],
                    form=form
                )
        return data
