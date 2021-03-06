from collections import namedtuple
from typing import List, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import RedirectView

from dashboard.toolbar import NavItem


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


class BaseDashboardMixin(LoginRequiredMixin, BreadcrumbMixin):

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(
            nav_items=(
                NavItem(label='Pivot', icon='fa fa-table', url=reverse('dashboard:category-tables'), active=reverse('dashboard:category-tables') in self.request.path),
                NavItem(label='Products', icon='fa fa-shopping-cart', url=reverse('dashboard:products'), active=reverse('dashboard:products') in self.request.path),
            )
        )
        return data
