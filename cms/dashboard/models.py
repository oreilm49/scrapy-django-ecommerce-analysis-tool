from typing import List, TYPE_CHECKING

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, Q
from django.utils.translation import gettext as _

from cms.dashboard.utils import average_price_gap
from cms.models import BaseModel, BaseQuerySet, Product
from cms.utils import is_value_numeric

if TYPE_CHECKING:
    from cms.models import ProductQuerySet


class CategoryTableQuerySet(BaseQuerySet):

    def for_user(self, user: User):
        """
        Returns all category tables in the user's company.
        """
        return self.filter(Q(user=user) | Q(user__profile__company=user.profile.company))


class CategoryTable(BaseModel):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name=_('Name'), max_length=100, help_text=_('The name for this dashboard'))
    x_axis_attribute = models.ForeignKey(
        "cms.AttributeType",
        verbose_name=_('X Axis Attribute'),
        help_text=_('The attribute used to group products into columns on the table.'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='category_tables_x_axis'
    )
    x_axis_values = models.JSONField(verbose_name=_('X Axis Values'), help_text=_('The values products must have for the x axis attribute in order to appear in the table.'), default=list)
    y_axis_attribute = models.ForeignKey(
        "cms.AttributeType",
        verbose_name=_('Y Axis Attribute'),
        help_text=_('The attribute used to group products into rows on the table.'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='category_tables_y_axis'
    )
    y_axis_values = models.JSONField(verbose_name=_('Y Axis Values'), help_text=_('The values products must have for the y axis attribute in order to appear in the table.'), default=list)
    category = models.ForeignKey("cms.Category", verbose_name=_('Category'), help_text=_('The category products should belong to in order to appear in the table.'), on_delete=models.SET_NULL, null=True)
    query = models.CharField(verbose_name=_('Search'), blank=True, null=True, max_length=100, help_text=_('General search text used to further filter products.'))

    objects = CategoryTableQuerySet.as_manager()

    def __str__(self):
        return self.name

    def products(self, queryset: 'ProductQuerySet') -> 'QuerySet':
        product_pks: List[int] = []
        if not is_value_numeric(self.x_axis_values[0]):
            products_from_attributes: 'ProductQuerySet' = self.x_axis_attribute.productattributes.filter(data__value__in=self.x_axis_values)
            product_pks.append(products_from_attributes.values_list('product', flat=True))
        if not is_value_numeric(self.y_axis_values[0]):
            products_from_attributes: 'ProductQuerySet' = self.y_axis_attribute.productattributes.filter(data__value__in=self.y_axis_values)
            product_pks.append(products_from_attributes.values_list('product', flat=True))
        if self.query:
            queryset = queryset.filter(model__contains=self.query)
        return queryset.filter(pk__in=product_pks, category=self.category)


class CategoryGapAnalysisQuerySet(BaseQuerySet):

    def for_user(self, user: User):
        """
        Returns all category tables in the user's company.
        """
        return self.filter(Q(user=user) | Q(user__profile__company=user.profile.company))


class CategoryGapAnalysisReport(BaseModel):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name=_('Name'), max_length=100, help_text=_('The name for this dashboard'))
    category = models.ForeignKey("cms.Category", verbose_name=_('Category'), help_text=_('The category products should belong to in order to appear in the table.'), on_delete=models.SET_NULL, null=True)
    brand = models.CharField(verbose_name=_('Brand'), max_length=100, help_text=_('The brand analysed in the gap analysis report.'))
    websites = models.ManyToManyField("cms.Website", verbose_name=_("Websites"), help_text=_('Limit gap analysis report to these websites.'))

    objects = CategoryGapAnalysisQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_products(self) -> List[Product]:
        products = Product.objects.pubished().filter(category=self.category)
        if self.websites:
            products = products.filter(websiteproductattributes__website__in=self.websites)
        return sorted([product for product in products], key=lambda product: product.current_average_price)

    def cluster_products(self):
        products: List[Product] = self.get_products()
        max_gap: float = average_price_gap(products)
        groups = [[products[0].current_average_price]]
        for product in products[1:]:
            if abs(product.current_average_price - groups[-1][-1]) <= max_gap:
                groups[-1].append(product.current_average_price)
            else:
                groups.append([product.current_average_price])
        return groups
