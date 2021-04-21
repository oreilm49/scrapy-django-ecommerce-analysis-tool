from typing import Optional, List

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from cms.dashboard.forms import CategoryGapAnalysisForm, CategoryGapAnalysisFilterForm
from cms.dashboard.models import CategoryGapAnalysisQuerySet, CategoryGapAnalysisReport
from cms.dashboard.toolbar import LinkButton, DropdownMenu, DropdownItem
from cms.dashboard.views.base import BaseDashboardMixin, Breadcrumb


class CategoryGapAnalysisReportMixin(BaseDashboardMixin):
    queryset: CategoryGapAnalysisQuerySet = CategoryGapAnalysisReport.objects.published().order_by('name')

    def get_queryset(self) -> CategoryGapAnalysisQuerySet:
        return self.queryset.for_user(self.request.user)


class CategoryGapAnalysisReports(CategoryGapAnalysisReportMixin, ListView):
    paginate_by = 10
    template_name = 'views/category_gap_analysis_reports.html'

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Category Gap Analysis", url=reverse('dashboard:category-gap-reports'), active=True),
        ]

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(
            action_item=LinkButton(
                label='New',
                url=reverse('dashboard:category-gap-report-create'),
                icon='fa fa-plus',
                btn_class='btn btn-primary btn-sm',
            ),
            filter_form=self.get_form(),
            header=_('Category Gap Analysis')
        )
        return data

    def get_form(self) -> CategoryGapAnalysisFilterForm:
        return CategoryGapAnalysisFilterForm(self.request.GET or None)

    def get_queryset(self) -> CategoryGapAnalysisQuerySet:
        queryset: CategoryGapAnalysisQuerySet = super().get_queryset()
        form: CategoryGapAnalysisFilterForm = self.get_form()
        if self.request.GET and form.is_valid():
            queryset: CategoryGapAnalysisQuerySet = form.search(queryset)
        return queryset


class CategoryGapAnalysisReportCreate(CategoryGapAnalysisReportMixin, SuccessMessageMixin, CreateView):
    template_name = 'views/category_gap_analysis_report_modify.html'
    form_class = CategoryGapAnalysisForm
    success_message = _('Successfully created "%(name)s"')

    @property
    def report(self) -> CategoryGapAnalysisReport:
        return self.object

    def get_success_url(self):
        return reverse('dashboard:category-gap-report', kwargs={'pk': self.report.pk})

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Category Gap Analysis", url=reverse('dashboard:category-gap-reports'), active=False),
            Breadcrumb(name="Create", url=reverse('dashboard:category-gap-report-create'), active=True),
        ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(header="Create New Category Gap Analysis Report")
        return data


class CategoryGapAnalysisReportUpdate(CategoryGapAnalysisReportMixin, SuccessMessageMixin, UpdateView):
    template_name = 'views/category_gap_analysis_report_modify.html'
    form_class = CategoryGapAnalysisForm
    success_message = _('Successfully updated "%(name)s"')

    @property
    def report(self) -> CategoryGapAnalysisReport:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(header=f"Edit {self.report.name}")
        return data

    @property
    def deleting(self):
        return self.request.POST.get('delete')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if self.deleting:
            report = self.report
            report.publish = False
            report.save()
            messages.success(request, _('Successfully deleted "{report}"').format(report=report))
            return HttpResponseRedirect(reverse('dashboard:category-gap-reports'))
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dashboard:category-gap-report', kwargs={'pk': self.report.pk})

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Category Gap Analysis", url=reverse('dashboard:category-gap-reports'), active=False),
            Breadcrumb(name=self.report.name, url=reverse('dashboard:category-gap-report', kwargs={'pk': self.report.pk}), active=False),
            Breadcrumb(name="Update", url=reverse('dashboard:category-gap-report-update', kwargs={'pk': self.report.pk}), active=True),
        ]


class CategoryGapAnalysisReportDetail(CategoryGapAnalysisReportMixin, DetailView):
    template_name = 'views/category_gap_analysis_report.html'

    @property
    def report(self) -> CategoryGapAnalysisReport:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            report=self.report,
            reports=self.get_queryset(),
            action_button=DropdownMenu(
                dropdown_icon='fas fa-cog fa-sm fa-fw text-gray-400',
                dropdown_id='tableEditDropdown',
                dropdown_class='btn-primary btn-sm',
                dropdown_label='Configure',
                items=[
                    DropdownItem(
                        url=reverse('dashboard:category-gap-report-update', kwargs={'pk': self.report.pk}),
                        icon='fas fa-pen fa-sm fa-fw text-gray-400',
                        label=_('Edit'),
                    ),
                    DropdownItem(
                        url=reverse('dashboard:category-gap-report-create'),
                        icon='fas fa-plus fa-sm fa-fw text-gray-400',
                        label=_('Create'),
                    ),
                ]
            ),
            **kwargs
        )

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Category Gap Analysis", url=reverse('dashboard:category-gap-reports'), active=False),
            Breadcrumb(name=self.report.name, url=reverse('dashboard:category-gap-report', kwargs={'pk': self.report.pk}), active=True),
        ]
