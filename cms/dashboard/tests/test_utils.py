from typing import List

from django.test import TestCase
from model_mommy import mommy

from cms.dashboard.models import CategoryGapAnalysisReport
from cms.dashboard.utils import average_price_gap
from cms.models import Product, WebsiteProductAttribute, AttributeType


class TestModels(TestCase):

    def test_average_price_gap(self):
        report: CategoryGapAnalysisReport = mommy.make(CategoryGapAnalysisReport, category__name="washers")
        price_attr: AttributeType = mommy.make(AttributeType, name="price")
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, data={'value': 200})
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, data={'value': 150})
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, data={'value': 100})
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, data={'value': 50})
        products: List[Product] = report.get_products()
        self.assertEqual(average_price_gap(products), 50)
