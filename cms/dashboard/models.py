import itertools
from typing import List, Iterator, Any, Optional, Dict

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from cms.dashboard.constants import CategoryTableProduct, CategoryTableEmpty
from cms.dashboard.reports import ProductCluster
from cms.models import BaseModel, BaseQuerySet, Product, ProductQuerySet, ProductAttributeQuerySet, ProductAttribute
from cms.utils import is_value_numeric, products_grouper


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

    def get_products(self, queryset: 'ProductQuerySet') -> 'ProductQuerySet':
        if self.query:
            queryset = queryset.filter(model__contains=self.query)
        if self.websites.exists():
            queryset = queryset.filter(websiteproductattributes__website__in=self.websites.all())
        if self.price_low:
            queryset = queryset.filter(websiteproductattributes__attribute_type__name='price',
                                       websiteproductattributes__data__value__gte=self.price_low)
        if self.price_high:
            queryset = queryset.filter(websiteproductattributes__attribute_type__name='price',
                                       websiteproductattributes__data__value__lte=self.price_high)
        if self.brands:
            queryset = queryset.filter(productattributes__attribute_type__name='brand',
                                       productattributes__data__value__in=self.brands)
        if self.products.exists():
            queryset = queryset.filter(pk__in=self.products.all())
        product_pks: List[int] = []
        if self.x_axis_values and not is_value_numeric(self.x_axis_values[0]):
            products_from_attributes: 'ProductQuerySet' = self.x_axis_attribute.productattributes.filter(data__value__in=self.x_axis_values)
            product_pks.append(products_from_attributes.values_list('product', flat=True))
        if self.y_axis_values and not is_value_numeric(self.y_axis_values[0]):
            products_from_attributes: 'ProductQuerySet' = self.y_axis_attribute.productattributes.filter(data__value__in=self.y_axis_values)
            product_pks.append(products_from_attributes.values_list('product', flat=True))
        if product_pks:
            queryset = queryset.filter(pk__in=product_pks)
        return queryset.filter(category=self.category, websiteproductattributes__data__value__isnull=False).distinct()

    def build_table(self, queryset: ProductQuerySet):
        """
        Builds a dict of product lists, grouped by y_axis_grouper and ordered by price.
        """
        products: List[CategoryTableProduct] = [CategoryTableProduct(
            x_axis_grouper=products_grouper(product, self.x_axis_attribute, self.x_axis_values),
            y_axis_grouper=products_grouper(product, self.y_axis_attribute, self.y_axis_values),
            product=product
        ) for product in self.get_products(queryset)]
        products = sorted([product for product in products], key=lambda product: product.product.current_average_price_int)
        if not self.y_axis_attribute:
            return {None: products}
        products_grid: Dict[str, List] = {y_axis_grouper: [] for y_axis_grouper in self.y_axis_values}
        col_index: int = 0
        col_min_val: int = 0
        col_grouper: Optional[str] = None

        def add_empty_cells_at_col_index(x_axis_grouper, grouper_exception: Optional[str] = None) -> None:
            for grouper, cell_list in products_grid.items():
                if grouper == grouper_exception:
                    continue
                try:
                    cell_list[col_index]
                except IndexError:
                    products_grid[grouper].append(CategoryTableEmpty(y_axis_grouper=grouper, x_axis_grouper=x_axis_grouper))

        for product in products:
            product_grouper = product.y_axis_grouper
            if not product_grouper:
                continue
            if col_min_val == 0:
                products_grid[product_grouper].append(product)
                col_min_val = product.product.current_average_price_int
                col_grouper = product_grouper
                continue

            price_pc_vs_min_val: int = int(((product.product.current_average_price_int - col_min_val) * 100) / col_min_val)
            if price_pc_vs_min_val <= 5:
                products_grid[product_grouper].append(product)
                if len(products_grid[product_grouper]) > (col_index + 1) and col_grouper == product_grouper:
                    add_empty_cells_at_col_index(product.x_axis_grouper)
                    col_index += 1
                    col_min_val = product.product.current_average_price_int
            elif price_pc_vs_min_val > 5:
                add_empty_cells_at_col_index(product.x_axis_grouper)
                products_grid[product_grouper].append(product)
                col_index += 1
                col_min_val = product.product.current_average_price_int
                col_grouper = product_grouper
        return products_grid


class CategoryTableAttribute(BaseModel):

    table = models.ForeignKey(CategoryTable, verbose_name=_("Table"), on_delete=models.CASCADE, related_name='category_table_attributes')
    attribute = models.ForeignKey("cms.AttributeType", verbose_name=_('Spec'), help_text=_('A spec to be displayed on the table.'), on_delete=models.SET_NULL, null=True, related_name='category_table_attributes')

    def __str__(self):
        return self.attribute


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
