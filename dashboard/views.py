import itertools
from collections import namedtuple
from typing import Iterator, Tuple, List, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView

from dashboard.forms import CategoryTableForm
from cms.models import Product
from cms.utils import products_grouper
from dashboard.models import CategoryTable, CategoryTableQuerySet
from dashboard.toolbar import ToolbarItem

CategoryTableProduct = namedtuple('CategoryTableProduct', ['x_axis_grouper', 'y_axis_grouper', 'product'])


class DashboardHome(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('dashboard:category-tables')


Breadcrumb = namedtuple('breadcrumb', ['url', 'name', 'active'])


class BreadcrumbMixin:

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        """
        override this method to add breadcrumbs to template context.
        """
        return None

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(
            breadcrumbs=self.get_breadcrumbs()
        )
        return data


class CategoryTableMixin(LoginRequiredMixin, BreadcrumbMixin):
    queryset: CategoryTableQuerySet = CategoryTable.objects.published()

    def get_queryset(self) -> CategoryTableQuerySet:
        return self.queryset.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(
            toolbar_items=[ToolbarItem(
                label='Create',
                url=reverse('dashboard:category-table-create'),
                icon='fa fa-plus'
            )]
        )
        return data


class CategoryTables(CategoryTableMixin, ListView):
    template_name = 'views/category_tables.html'

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Pivot Tables", url=reverse('dashboard:category-tables'), active=True),
        ]


class CategoryTableCreate(CategoryTableMixin, SuccessMessageMixin, CreateView):
    template_name = 'views/category_table_modify.html'
    form_class = CategoryTableForm
    success_message = _('Sucessfully created "%(name)s"')

    @property
    def table(self) -> CategoryTable:
        return self.object

    def get_success_url(self):
        return reverse('dashboard:category-table', kwargs={'pk': self.table.pk})

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Pivot Tables", url=reverse('dashboard:category-tables'), active=False),
            Breadcrumb(name="Create", url=reverse('dashboard:category-table-create'), active=True),
        ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CategoryTableUpdate(CategoryTableMixin, SuccessMessageMixin, UpdateView):
    template_name = 'views/category_table_modify.html'
    form_class = CategoryTableForm
    success_message = _('Sucessfully updated "%(name)s"')

    @property
    def table(self) -> CategoryTable:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))

    @property
    def deleting(self):
        return self.request.POST.get('delete')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if self.deleting:
            table = self.table
            table.publish = False
            table.save()
            messages.success(request, _('Sucessfully deleted "{table}"').format(table=table))
            return HttpResponseRedirect(reverse('dashboard:category-tables'))
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dashboard:category-table', kwargs={'pk': self.table.pk})

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Pivot Tables", url=reverse('dashboard:category-tables'), active=False),
            Breadcrumb(name="Update", url=reverse('dashboard:category-table-update', kwargs={'pk': self.table.pk}), active=True),
        ]


class CategoryTableDetail(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    template_name = 'views/category_table.html'
    queryset: CategoryTableQuerySet = CategoryTable.objects.published()

    def get_queryset(self) -> CategoryTableQuerySet:
        return self.queryset.for_user(self.request.user)

    @property
    def table(self) -> CategoryTable:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))

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
            table=self.table,
            table_data=table_data,
            x_axis_values=self.table.x_axis_values,
        )
        return data

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Pivot Tables", url=reverse('dashboard:category-tables'), active=False),
            Breadcrumb(name=self.table.name, url=reverse('dashboard:category-table', kwargs={'pk': self.table.pk}), active=True),
        ]
