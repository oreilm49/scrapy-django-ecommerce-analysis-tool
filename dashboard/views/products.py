from typing import Optional, List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView

from cms.models import Product, ProductQuerySet, WebsiteProductAttributeQuerySet, WebsiteProductAttribute
from dashboard.views.base import Breadcrumb, BreadcrumbMixin


class Products(LoginRequiredMixin, BreadcrumbMixin, ListView):
    paginate_by = 25
    queryset: ProductQuerySet = Product.objects.published()
    template_name = 'views/products.html'

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Products", url=reverse('dashboard:products'), active=True),
        ]


class ProductDetail(LoginRequiredMixin, BreadcrumbMixin, ListView):
    paginate_by = 25
    template_name = 'views/product.html'
    queryset: WebsiteProductAttributeQuerySet = WebsiteProductAttribute.objects.published()

    def get_queryset(self):
        return super().get_queryset().filter(product=self.product, attribute_type__name="price")

    @property
    def product(self) -> Product:
        return get_object_or_404(Product.objects.published(), pk=self.request.resolver_match.kwargs.get('pk'))

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Products", url=reverse('dashboard:products'), active=False),
            Breadcrumb(name=self.product.model, url=reverse('dashboard:product', kwargs={'pk': self.product.pk}), active=True),
        ]
