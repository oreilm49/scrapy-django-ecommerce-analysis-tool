from typing import List

from cms.models import Product, ProductQuerySet


class ProductCluster:
    """
    Given a list of products, returns gap analysis
    """

    def __init__(self, target_range: ProductQuerySet, products: List[Product]):
        self.products = products
        self.target_range = target_range

    def dominant_specs(self):
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
