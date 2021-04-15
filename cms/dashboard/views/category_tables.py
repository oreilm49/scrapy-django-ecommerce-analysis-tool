from typing import List, Optional

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from cms.dashboard.forms import CategoryTableFilterForm, CategoryTableForm, get_category_table_attribute_formset
from cms.dashboard.models import CategoryTableQuerySet, CategoryTable, CategoryTableAttribute
from cms.models import Product
from cms.dashboard.toolbar import LinkButton
from cms.dashboard.views.base import Breadcrumb, BaseDashboardMixin


class CategoryTableMixin(BaseDashboardMixin):
    queryset: CategoryTableQuerySet = CategoryTable.objects.published().order_by('name')

    def get_queryset(self) -> CategoryTableQuerySet:
        return self.queryset.for_user(self.request.user)


class CategoryTables(CategoryTableMixin, ListView):
    paginate_by = 10
    template_name = 'views/category_tables.html'

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Pivot Tables", url=reverse('dashboard:category-tables'), active=True),
        ]

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(
            card_action_button=LinkButton(
                label='New',
                url=reverse('dashboard:category-table-create'),
                icon='fa fa-plus',
                btn_class='btn btn-primary btn-sm',
            ),
            filter_form=self.get_form()
        )
        return data

    def get_form(self) -> CategoryTableFilterForm:
        return CategoryTableFilterForm(self.request.GET or None)

    def get_queryset(self) -> CategoryTableQuerySet:
        queryset: CategoryTableQuerySet = super().get_queryset()
        form: CategoryTableFilterForm = self.get_form()
        if self.request.GET and form.is_valid():
            queryset: CategoryTableQuerySet = form.search(queryset)
        return queryset


class CategoryTableCreate(CategoryTableMixin, SuccessMessageMixin, CreateView):
    template_name = 'views/category_table_modify.html'
    form_class = CategoryTableForm
    success_message = _('Successfully created "%(name)s"')

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

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(header="Create New Pivot Table")
        return data


class CategoryTableUpdate(CategoryTableMixin, SuccessMessageMixin, UpdateView):
    template_name = 'views/category_table_modify.html'
    form_class = CategoryTableForm
    success_message = _('Successfully updated "%(name)s"')

    @property
    def table(self) -> CategoryTable:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(header=f"Edit {self.table.name}")
        return data

    @property
    def deleting(self):
        return self.request.POST.get('delete')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if self.deleting:
            table = self.table
            table.publish = False
            table.save()
            messages.success(request, _('Successfully deleted "{table}"').format(table=table))
            return HttpResponseRedirect(reverse('dashboard:category-tables'))
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dashboard:category-table', kwargs={'pk': self.table.pk})

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Pivot Tables", url=reverse('dashboard:category-tables'), active=False),
            Breadcrumb(name="Update", url=reverse('dashboard:category-table-update', kwargs={'pk': self.table.pk}), active=True),
        ]


class CategoryTableDetail(BaseDashboardMixin, DetailView):
    template_name = 'views/category_table.html'
    queryset: CategoryTableQuerySet = CategoryTable.objects.published()

    def get_queryset(self) -> CategoryTableQuerySet:
        return self.queryset.for_user(self.request.user)

    @property
    def table(self) -> CategoryTable:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            table=self.table,
            table_data=self.table.build_table(Product.objects.published()),
            x_axis_values=self.table.x_axis_values,
            card_action_button=LinkButton(
                url=reverse('dashboard:category-table-update', kwargs={'pk': self.table.pk}),
                icon='fas fa-pen fa-sm fa-fw text-gray-400',
            ),
            **kwargs
        )

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Pivot Tables", url=reverse('dashboard:category-tables'), active=False),
            Breadcrumb(name=self.table.name, url=reverse('dashboard:category-table', kwargs={'pk': self.table.pk}), active=True),
        ]


class CategoryTableAttributeUpdate(CategoryTableMixin, SuccessMessageMixin, UpdateView):
    template_name = 'views/category_table_specs_modify.html'
    success_message = _('Category table specs updated successfully')

    @property
    def table(self) -> CategoryTable:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))

    def get_success_url(self):
        return reverse('dashboard:category-table', kwargs={'pk': self.table.pk})

    def get_form(self, form_class=None):
        return get_category_table_attribute_formset()(self.request.POST or None, queryset=CategoryTableAttribute.objects.published().filter(table=self.table))

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            table=self.table,
            formset=self.get_form(),
            header=_('Update table specs'),
            **kwargs
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        formset = self.get_form()
        if not formset.is_valid():
            messages.error(request, _('There was an error processing product attributes'))
            return render(request, self.template_name, {'formset': formset})
        for form in formset.save(commit=False):
            form.table = self.table
            form.save()
        formset.save_m2m()
        return self.form_valid(formset)
