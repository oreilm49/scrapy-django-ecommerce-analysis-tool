from typing import List, TYPE_CHECKING

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, Q
from django.utils.translation import gettext as _

from cms.models import BaseModel, BaseQuerySet
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
        help_text=_('The attribute used to group products into rows on the table.'),
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
