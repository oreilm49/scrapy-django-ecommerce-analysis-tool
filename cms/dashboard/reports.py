from itertools import groupby
from operator import itemgetter
from typing import List, Dict, Union

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
        return

    def dominant_brands(self):
        """Gets the most common brands for this pricepoint"""
        return

    def pricepoint(self):
        """The common pricepoint that groups all products"""
        return

    def target_range_spec_gap(self):
        """
        given the target range, are there any gaps
        vs the dominant specs for the category
        """
        return
