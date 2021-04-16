import datetime
from typing import Optional, List, Dict

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from django.utils.translation import gettext as _

from cms.dashboard.toolbar import LinkButton
from cms.models import Product, ProductQuerySet, WebsiteProductAttributeQuerySet, WebsiteProductAttribute
from cms.dashboard.forms import ProductsFilterForm, ProductPriceFilterForm
from cms.dashboard.views.base import Breadcrumb, BaseDashboardMixin
from cms.dashboard.utils import line_chart


class Products(BaseDashboardMixin, ListView):
    paginate_by = 10
    queryset: ProductQuerySet = Product.objects.published()
    template_name = 'views/products.html'

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Products", url=reverse('dashboard:products'), active=True),
        ]

    def get_form(self) -> ProductsFilterForm:
        return ProductsFilterForm(self.request.GET or None)

    def get_queryset(self) -> ProductQuerySet:
        queryset: ProductQuerySet = super().get_queryset()
        form: ProductsFilterForm = self.get_form()
        if self.request.GET and form.is_valid():
            queryset: ProductQuerySet = form.search(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(filter_form=self.get_form(), header=_('Products'))
        return data


class ProductDetail(BaseDashboardMixin, ListView):
    paginate_by = 25
    template_name = 'views/product.html'
    queryset: WebsiteProductAttributeQuerySet = WebsiteProductAttribute.objects.published().filter(attribute_type__name="price").order_by('-created')

    def get_queryset(self):
        qs = super().get_queryset().filter(product=self.product)
        form: ProductPriceFilterForm = self.get_form()
        if form.is_valid():
            qs = form.search(qs)
        return qs

    def get_form(self):
        return ProductPriceFilterForm(self.request.GET or None)

    @property
    def product(self) -> Product:
        return get_object_or_404(Product.objects.published(), pk=self.request.resolver_match.kwargs.get('pk'))

    def get_breadcrumbs(self) -> Optional[List[Breadcrumb]]:
        return [
            Breadcrumb(name="Products", url=reverse('dashboard:products'), active=False),
            Breadcrumb(name=self.product.model, url=reverse('dashboard:product', kwargs={'pk': self.product.pk}), active=True),
        ]

    def get_price_chart(self) -> Dict:
        return line_chart(
            self.product.price_history(datetime.datetime.now() - datetime.timedelta(days=7)),
            title="7 Day price history",
            x_label='day',
            x='created',
            y_label='price',
            y='price',
        )

    def get_context_data(self, **kwargs):
        data: dict = super().get_context_data(**kwargs)
        data.update(product=self.product, filter_form=self.get_form(), price_chart=self.get_price_chart())
        if self.request.user.is_superuser:
            data.update(
                edit_spec_button=LinkButton(
                    url=reverse('admin:cms_product_change', kwargs={'object_id': self.product.pk}),
                    icon='fas fa-pen fa-sm fa-fw text-gray-400',
                )
            )
        return data
