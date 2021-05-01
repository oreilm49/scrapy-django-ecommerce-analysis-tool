from django.test import TestCase
from model_mommy import mommy

from cms.data_processing.utils import create_product_attribute
from cms.models import Product, ProductAttribute, Unit, Category


class TestModels(TestCase):

    def test_product_create_attribute(self):
        category: Category = mommy.make(Category, name="washing machines")
        product: Product = mommy.make(Product, category=category)
        with self.subTest("unit"):
            self.assertFalse(ProductAttribute.objects.filter(product=product, attribute_type__name='Wash capacity', attribute_type__category=category).exists())
            self.assertFalse(Unit.objects.filter(name="kilogram").first())
            create_product_attribute(product, 'Wash capacity', '10kg')
            self.assertTrue(ProductAttribute.objects.filter(product=product, attribute_type__name='Wash capacity', attribute_type__category=category, data__value=10).exists())
            self.assertTrue(Unit.objects.filter(name="kilogram").first())
        with self.subTest("range unit"):
            self.assertFalse(ProductAttribute.objects.filter(product=product, attribute_type__name='power - low', attribute_type__category=category).exists())
            self.assertFalse(ProductAttribute.objects.filter(product=product, attribute_type__name='power - high', attribute_type__category=category).exists())
            self.assertFalse(Unit.objects.filter(name="volt").first())
            create_product_attribute(product, 'power', '220 - 240v')
            self.assertTrue(ProductAttribute.objects.filter(product=product, attribute_type__name='power - low', attribute_type__category=category, data__value=220).exists())
            self.assertTrue(ProductAttribute.objects.filter(product=product, attribute_type__name='power - high', attribute_type__category=category, data__value=240).exists())
            self.assertTrue(Unit.objects.filter(name="volt").first())
        with self.subTest("energy rating"):
            self.assertFalse(ProductAttribute.objects.filter(product=product, attribute_type__name='energy rating', attribute_type__category=category).exists())
            create_product_attribute(product, 'energy rating', 'a+++')
            self.assertTrue(ProductAttribute.objects.filter(product=product, attribute_type__name='energy rating', attribute_type__category=category, data__value="a+++").exists())
