from itertools import groupby
from operator import itemgetter
from statistics import mean
from typing import List, Dict, Union, Optional, Iterator, Tuple

from django.utils.functional import cached_property

from cms.dashboard.constants import COMPETITIVE_SCORE_GOOD, COMPETITIVE_SCORE_BAD, COMPETITIVE_SCORE_ATTENTION
from cms.models import Product, ProductQuerySet, Category, CategoryAttributeConfig, ProductAttribute, \
    ProductAttributeQuerySet, Brand

DominantSpecs = Dict[CategoryAttributeConfig, Dict[str, Union[int, float, str]]]
ProductSpecValues = List[Dict[CategoryAttributeConfig, Union[str, float, int, bool]]]
Price = Union[float, int]


class ProductCluster:
    """
    Given a list of products, returns gap analysis
    """

    def __init__(self, category: Category, products_grouper: Tuple[Price, Iterator], target_range: ProductQuerySet, total_number_products: int):
        products: List[Product] = list(products_grouper[1])
        self.category: Category = category
        self.products: ProductQuerySet = Product.objects.filter(category=self.category, pk__in=[product.pk for product in products])
        self.target_range: ProductQuerySet = target_range.filter(pk__in=self.products)
        self.cluster_size = "{size}%".format(size=int((len(products) / total_number_products)*100))
        self.cluster_price = products_grouper[0]

    def get_product_spec_values(self) -> ProductSpecValues:
        """Returns a list of dicts of the spec values for each product."""
        spec_values: ProductSpecValues = []
        for product in self.products:
            product_specs = {}
            for attribute_config in product.category.category_attribute_configs.order_by('order').iterator():
                attribute_config: 'CategoryAttributeConfig'
                product_attr: ProductAttribute = attribute_config.attribute_type.productattributes.filter(product__pk=product.pk).first()
                if product_attr:
                    product_specs[attribute_config] = product_attr.data['value']
            if product_specs:
                spec_values.append(product_specs)
        return spec_values

    def dominant_specs(self) -> DominantSpecs:
        """Gets the most common spec combinations for this pricepoint"""
        dominant_specs: DominantSpecs = {}
        products_with_specs: ProductSpecValues = self.get_product_spec_values()
        if not products_with_specs:
            return dominant_specs
        for category_spec_config in products_with_specs[0].keys():
            sorted_products = sorted([product for product in products_with_specs if product.get(category_spec_config)], key=lambda product: product[category_spec_config])
            ranked_spec_values = list((spec_value, sum(1 for _ in products)) for spec_value, products in
                                      groupby(sorted_products, key=lambda product: product[category_spec_config]))
            if ranked_spec_values:
                dominant_spec = max(ranked_spec_values, key=itemgetter(1))
                dominant_specs[category_spec_config] = {'value': dominant_spec[0], 'number_of_products': dominant_spec[1]}
        return dominant_specs

    @cached_property
    def dominant_brand(self) -> Optional[Dict[str, Union[str, int]]]:
        """Gets the most common brands for this pricepoint"""
        sorted_products = sorted([product for product in self.products if product.brand], key=lambda product: product.brand.pk)
        ranked_brands = tuple((brand, sum(1 for _ in products)) for brand, products in groupby(sorted_products, key=lambda product: product.brand.pk))
        if ranked_brands:
            dominant_brand_id, num_products = max(ranked_brands, key=itemgetter(1))
            dominant_brand: Brand = Brand.objects.get(pk=dominant_brand_id)
            display_share = '{:.0%}'.format(num_products / self.products.count()) if self.products.exists() else None
            target_range_display_share = '{:.0%}'.format(self.target_range.count() / self.products.count()) if self.products.exists() else None
            return {
                'value': dominant_brand,
                'number_of_products': num_products,
                'display_share': display_share,
                'target_range_display_share': target_range_display_share,
            }

    @cached_property
    def average_price(self) -> Optional[int]:
        prices: List[Optional[int]] = [product.current_average_price_int for product in self.products if product.current_average_price_int]
        return int(mean(prices)) if prices else None

    @cached_property
    def target_range_spec_gap(self) -> DominantSpecs:
        """
        given the target range, are there any gaps
        vs the dominant specs for the category
        """
        dominant_specs: DominantSpecs = self.dominant_specs()
        for category_spec_config, spec_data in dominant_specs.items():
            product_specs: ProductAttributeQuerySet = ProductAttribute.objects.filter(product__in=self.target_range, attribute_type=category_spec_config.attribute_type)
            filter_kwargs: Dict = category_spec_config.product_attribute_data_filter_kwargs(spec_data['value'])
            product_specs: ProductAttributeQuerySet = getattr(product_specs, category_spec_config.product_attribute_data_filter_or_exclude)(**filter_kwargs)
            dominant_specs[category_spec_config]['target_range_products'] = product_specs.products()
        return dominant_specs

    @cached_property
    def competitive_score(self) -> Optional[str]:
        """An overall competitive score for the target range within the cluster."""
        dominant_specs_number = 0
        matched_target_range = 0
        for spec in self.target_range_spec_gap.keys():
            spec: CategoryAttributeConfig
            dominant_specs_number += 1
            if self.target_range_spec_gap[spec]['target_range_products'].exists():
                matched_target_range += 1
        if not dominant_specs_number:
            return
        competitive_on_specs: bool = (matched_target_range / dominant_specs_number) == 1
        dominant_brand_in_target_range: bool = self.dominant_brand['value'] in list(self.target_range.brands()) if self.dominant_brand else False
        if competitive_on_specs and dominant_brand_in_target_range:
            return COMPETITIVE_SCORE_GOOD
        elif not competitive_on_specs and not dominant_brand_in_target_range:
            return COMPETITIVE_SCORE_BAD
        else:
            return COMPETITIVE_SCORE_ATTENTION
