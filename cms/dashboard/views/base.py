from collections import namedtuple
from typing import List, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import RedirectView

from cms.dashboard.forms import FeedbackForm
from cms.dashboard.toolbar import NavItem
from cms.settings import ADMINS
from cms.tasks import send_email


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
                NavItem(label='Category Tables', icon='fa fa-table', url=reverse('dashboard:category-tables'), active=reverse('dashboard:category-tables') in self.request.path),
                NavItem(label='Products', icon='fa fa-shopping-cart', url=reverse('dashboard:products'), active=reverse('dashboard:products') in self.request.path),
                NavItem(label='Gap Analysis', icon='fa fa-filter', url=reverse('dashboard:category-gap-reports'), active=reverse('dashboard:category-gap-reports') in self.request.path),
            ),
            feedback_form=FeedbackForm()
        )
        return data


class ProcessFeedback(LoginRequiredMixin, View):

    def post(self, request):
        form: FeedbackForm = FeedbackForm(request.POST or None)
        if form.is_valid():
            messages.success(request, _('Thanks for the feedback!'))
            send_email.delay('Feedback', form.cleaned_data['feedback'], [email for name, email in ADMINS])
        else:
            messages.error(request, _('There was an error processing your feedback. If this persists, please contact support directly at info@specr.ie'))
        return HttpResponseRedirect(reverse("dashboard:home"))
