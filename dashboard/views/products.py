from typing import Optional, List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView

from cms.models import Product, ProductQuerySet
from dashboard.views.base import Breadcrumb, BreadcrumbMixin


class Products(LoginRequiredMixin, BreadcrumbMixin, ListView):
    paginate_by = 25
    queryset: ProductQuerySet = Product.objects.published()
    template_name = 'views/products.html'

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Products", url=reverse('dashboard:products'), active=True),
        ]


class ProductDetail(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    template_name = 'views/product.html'
    queryset: ProductQuerySet = Product.objects.published()

    def get_queryset(self) -> ProductQuerySet:
        return self.queryset.for_user(self.request.user)

    @property
    def product(self) -> Product:
        return get_object_or_404(self.queryset, pk=self.request.resolver_match.kwargs.get('pk'))
