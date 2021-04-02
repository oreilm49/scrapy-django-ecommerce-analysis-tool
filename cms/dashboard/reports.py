from itertools import groupby
from operator import itemgetter
from statistics import mean
from typing import List, Dict, Union, Optional

from cms.models import Product, ProductQuerySet, Category, CategoryAttributeConfig, ProductAttribute


class ProductCluster:
    """
    Given a list of products, returns gap analysis
    """

    def __init__(self, category: Category, products: Union[List[Product], ProductQuerySet]):
        self.products = products
        self.category = category

    def get_product_spec_values(self) -> List[Dict[str, Union[str, float, int, bool]]]:
        """Returns a list of dicts of the spec values for each product."""
        spec_values: List[Dict[str, Union[str, float, int, bool]]] = []
        for product in self.products:
            assert product.category == self.category, f"Product used from incorrect category: {product.category}."
            product_specs = {}
            for attribute_config in product.category.category_attribute_configs.order_by('order').iterator():
                attribute_config: 'CategoryAttributeConfig'
                product_attr: ProductAttribute = attribute_config.attribute_type.productattributes.filter(product__pk=product.pk).first()
                if product_attr:
                    product_specs[attribute_config.attribute_type.name] = product_attr.data['value']
            if product_specs:
                spec_values.append(product_specs)
        return spec_values

    def dominant_specs(self) -> Dict[str, Dict[str, Union[int, float, str]]]:
        """Gets the most common spec combinations for this pricepoint"""
        dominant_specs = {}
        products_with_specs: List[Dict] = self.get_product_spec_values()
        if not products_with_specs:
            return dominant_specs
        for spec_name in products_with_specs[0].keys():
            sorted_products = sorted(products_with_specs, key=lambda product: product[spec_name])
            ranked_spec_values = ((spec_value, sum(1 for _ in products)) for spec_value, products in
                                  groupby(sorted_products, key=lambda product: product[spec_name]))
            dominant_spec = max(ranked_spec_values, key=itemgetter(1))
            dominant_specs[spec_name] = {'value': dominant_spec[0], 'number_of_products': dominant_spec[1]}
        return dominant_specs

    def dominant_brands(self) -> Optional[Dict[str, Union[str, int]]]:
        """Gets the most common brands for this pricepoint"""
        sorted_products = sorted(self.products, key=lambda product: product.brand)
        ranked_brands = ((brand, sum(1 for _ in products)) for brand, products in
                              groupby(sorted_products, key=lambda product: product.brand))
        if ranked_brands:
            dominant_brand = max(ranked_brands, key=itemgetter(0))
            return {'value': dominant_brand[0], 'number_of_products': dominant_brand[1]}

    def average_price(self) -> Optional[int]:
        prices: List[Optional[int]] = [product.current_average_price_int for product in self.products if product.current_average_price_int]
        return int(mean(prices)) if prices else None

    def target_range_spec_gap(self):
        """
        given the target range, are there any gaps
        vs the dominant specs for the category
        """
        return
