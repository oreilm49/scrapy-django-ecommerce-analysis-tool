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
