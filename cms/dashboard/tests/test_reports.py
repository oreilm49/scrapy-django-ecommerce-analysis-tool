from typing import Optional

from django.test import TestCase
from model_mommy import mommy

from cms.dashboard.reports import ProductCluster
from cms.models import Product, ProductAttribute, Category, CategoryAttributeConfig, AttributeType


class TestReports(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # set up category
        cls.category: Category = mommy.make(Category, name="washers")
        cls.cat_cfg_1: CategoryAttributeConfig = mommy.make(CategoryAttributeConfig, attribute_type__name="load size", order=1, category=cls.category)
        cls.cat_cfg_2: CategoryAttributeConfig = mommy.make(CategoryAttributeConfig, attribute_type__name="spin", order=2, category=cls.category)
        cls.cat_cfg_3: CategoryAttributeConfig = mommy.make(CategoryAttributeConfig, attribute_type__name="energy usage", order=3, category=cls.category)
        cls.brand_attr: AttributeType = mommy.make(AttributeType, name="brand")

        def make_product(load_size: int, spin: int, energy: int, order: int, brand: Optional[str] = None) -> Product:
            product: Product = mommy.make(Product, category=cls.category, order=order)
            mommy.make(ProductAttribute, product=product, attribute_type=cls.cat_cfg_1.attribute_type, data={'value': load_size})
            mommy.make(ProductAttribute, product=product, attribute_type=cls.cat_cfg_2.attribute_type, data={'value': spin})
            mommy.make(ProductAttribute, product=product, attribute_type=cls.cat_cfg_3.attribute_type, data={'value': energy})
            if brand:
                mommy.make(ProductAttribute, product=product, attribute_type=cls.brand_attr, data={'value': brand})
            return product

        make_product(7, 1400, 50, 1, brand="whirlpool")
        make_product(8, 1400, 75, 2, brand="whirlpool")
        make_product(8, 1600, 100, 3, brand="hotpoint")
        make_product(6, 1200, 100, 4, brand="indesit")

    def test_product_cluster_get_product_spec_values(self):
        with self.subTest("incorrect category for products"):
            cluster: ProductCluster = ProductCluster(mommy.make(Category), [mommy.make(Product, category__name="test")])
            with self.assertRaises(AssertionError) as context:
                cluster.get_product_spec_values()
            self.assertEqual(str(context.exception), "Product used from incorrect category: test.")

        with self.subTest("empty product queryset"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.none())
            product_spec_values = cluster.get_product_spec_values()
            self.assertEqual(product_spec_values, [])

        with self.subTest("spec values"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.filter(category=self.category).order_by('order'))
            product_spec_values = cluster.get_product_spec_values()
            self.assertIsInstance(product_spec_values, list)
            self.assertEqual(product_spec_values[0], {
                'load size': 7,
                'spin': 1400,
                'energy usage': 50,
            })
            self.assertEqual(product_spec_values[-1], {
                'load size': 6,
                'spin': 1200,
                'energy usage': 100,
            })

        with self.subTest("No spec values"):
            ProductAttribute.objects.all().delete()
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.filter(category=self.category).order_by('order'))
            product_spec_values = cluster.get_product_spec_values()
            self.assertEqual(product_spec_values, [])

    def test_dominant_specs(self):
        cluster: ProductCluster = ProductCluster(self.category, Product.objects.filter(category=self.category).order_by('order'))
        dominant_specs = cluster.dominant_specs()
        self.assertEqual(dominant_specs['load size'], {'value': 8, 'number_of_products': 2})
        self.assertEqual(dominant_specs['spin'], {'value': 1400, 'number_of_products': 2})
        self.assertEqual(dominant_specs['energy usage'], {'value': 100, 'number_of_products': 2})

        with self.subTest("empty queryset"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.none())
            self.assertEqual(cluster.dominant_specs(), {})

    def test_dominant_brands(self):
        cluster: ProductCluster = ProductCluster(self.category, Product.objects.filter(category=self.category).order_by('order'))
        self.assertEqual(cluster.dominant_brands(), {'value': "whirlpool", 'number_of_products': 2})

        with self.subTest("empty queryset"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.none())
            self.assertEqual(cluster.dominant_brands(), {})
