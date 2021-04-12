import itertools
from typing import List, Iterator, Any

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet, Q
from django.utils.translation import gettext as _

from cms.dashboard.reports import ProductCluster
from cms.models import BaseModel, BaseQuerySet, Product, ProductQuerySet, ProductAttributeQuerySet, ProductAttribute
from cms.utils import is_value_numeric


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
    websites = models.ManyToManyField("cms.Website", verbose_name=_("Websites"), help_text=_('Only show products that are on these websites.'))
    brands = models.JSONField(verbose_name=_('Brands'), help_text=_('Only show products for these brands.'), default=list, blank=True, null=True)
    products = models.ManyToManyField("cms.Product", verbose_name=_("Products"), help_text=_('Only show these products.'))
    price_low = models.FloatField(verbose_name=_("Price low"), help_text=_("Only show products above this price"), blank=True, null=True)
    price_high = models.FloatField(verbose_name=_("Price high"), help_text=_("Only show products below this price"), blank=True, null=True)

    objects = CategoryTableQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_products(self, queryset: 'ProductQuerySet') -> 'QuerySet':
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
    price_clusters = models.JSONField(verbose_name=_('Price clusters'), help_text=_('Price levels used to cluster products.'), default=list)

    objects = CategoryGapAnalysisQuerySet.as_manager()

    def __str__(self):
        return self.name

    @property
    def products(self) -> ProductQuerySet:
        products = Product.objects.filter(category=self.category)
        if self.websites.exists():
            products = products.filter(websiteproductattributes__website__in=self.websites.all())
        return products

    @property
    def target_range(self) -> ProductQuerySet:
        brand_attributes: ProductAttributeQuerySet = ProductAttribute.objects.filter(attribute_type__name="brand", data__value=self.brand)
        return self.products.filter(pk__in=[product_attribute.product.pk for product_attribute in brand_attributes])

    def get_products(self) -> List[Product]:
        """Retrieves and sorts products relevant to report."""
        return sorted([product for product in self.products if product.current_average_price_int], key=lambda product: product.current_average_price_int)

    def cluster_products(self) -> Iterator[tuple[Any, Iterator[Product]]]:
        """Clusters products by pricepoint."""
        products: List[Product] = self.get_products()

        def product_price_grouper(product: Product):
            for price in self.price_clusters:
                if product.current_average_price_int <= price:
                    return price
        return itertools.groupby(products, key=lambda product: product_price_grouper(product))

    @property
    def gap_analysis_clusters(self) -> List[ProductCluster]:
        return [ProductCluster(self.category, products, self.target_range, self.products.count()) for products in self.cluster_products()]
