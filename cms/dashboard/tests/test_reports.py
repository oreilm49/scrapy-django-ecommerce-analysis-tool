from typing import Optional

from django.test import TestCase
from model_mommy import mommy

from cms.constants import SCORING_NUMERICAL_HIGHER, SCORING_NUMERICAL_LOWER
from cms.dashboard.reports import ProductCluster
from cms.models import Product, ProductAttribute, Category, CategoryAttributeConfig, AttributeType, \
    WebsiteProductAttribute, ProductQuerySet


class TestReports(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # set up category
        cls.category: Category = mommy.make(Category, name="washers")
        cls.cat_cfg_1: CategoryAttributeConfig = mommy.make(CategoryAttributeConfig, attribute_type__name="load size", order=1, category=cls.category, scoring=SCORING_NUMERICAL_HIGHER)
        cls.cat_cfg_2: CategoryAttributeConfig = mommy.make(CategoryAttributeConfig, attribute_type__name="spin", order=2, category=cls.category, scoring=SCORING_NUMERICAL_HIGHER)
        cls.cat_cfg_3: CategoryAttributeConfig = mommy.make(CategoryAttributeConfig, attribute_type__name="energy usage", order=3, category=cls.category, scoring=SCORING_NUMERICAL_LOWER)
        cls.brand_attr: AttributeType = mommy.make(AttributeType, name="brand")
        cls.price_attr: AttributeType = mommy.make(AttributeType, name="price")

        def make_product(price: float, load_size: int, spin: int, energy: int, order: int, brand: Optional[str] = None) -> Product:
            product: Product = mommy.make(Product, category=cls.category, order=order)
            mommy.make(ProductAttribute, product=product, attribute_type=cls.cat_cfg_1.attribute_type, data={'value': load_size})
            mommy.make(ProductAttribute, product=product, attribute_type=cls.cat_cfg_2.attribute_type, data={'value': spin})
            mommy.make(ProductAttribute, product=product, attribute_type=cls.cat_cfg_3.attribute_type, data={'value': energy})
            if brand:
                mommy.make(ProductAttribute, product=product, attribute_type=cls.brand_attr, data={'value': brand})
            mommy.make(WebsiteProductAttribute, product=product, attribute_type=cls.price_attr, data={'value': price})
            return product

        cls.p1: Product = make_product(299.99, 7, 1400, 50, 1, brand="whirlpool")
        cls.p2: Product = make_product(399.99, 8, 1400, 75, 2, brand="whirlpool")
        cls.p3: Product = make_product(349.99, 8, 1600, 100, 3, brand="hotpoint")
        cls.p4: Product = make_product(399.99, 6, 1200, 100, 4, brand="indesit")
        cls.cluster: ProductCluster = ProductCluster(
            cls.category,
            [product for product in Product.objects.all()],
            Product.objects.filter(pk=cls.p1.pk)
        )

    def test_product_cluster_init(self):
        with self.subTest("target range"):
            self.assertIn(self.p1, self.cluster.target_range)
            self.assertNotIn(self.p2, self.cluster.target_range)
            self.assertNotIn(self.p3, self.cluster.target_range)
            self.assertNotIn(self.p4, self.cluster.target_range)
        with self.subTest("products"):
            self.assertIsInstance(self.cluster.products, ProductQuerySet)

    def test_product_cluster_get_product_spec_values(self):
        with self.subTest("incorrect category for products"):
            wrong_product: Product = mommy.make(Product, category__name="test")
            cluster: ProductCluster = ProductCluster(mommy.make(Category), [wrong_product], Product.objects.none())
            self.assertNotIn(wrong_product, cluster.products)
        with self.subTest("empty product queryset"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.none(), Product.objects.none())
            product_spec_values = cluster.get_product_spec_values()
            self.assertEqual(product_spec_values, [])

        with self.subTest("spec values"):
            product_spec_values = self.cluster.get_product_spec_values()
            self.assertIsInstance(product_spec_values, list)
            self.assertIn({
                self.cat_cfg_1: 7,
                self.cat_cfg_2: 1400,
                self.cat_cfg_3: 50,
            }, product_spec_values)
            self.assertIn({
                self.cat_cfg_1: 6,
                self.cat_cfg_2: 1200,
                self.cat_cfg_3: 100,
            }, product_spec_values)

        with self.subTest("No spec values"):
            ProductAttribute.objects.all().delete()
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.filter(category=self.category).order_by('order'), Product.objects.none())
            product_spec_values = cluster.get_product_spec_values()
            self.assertEqual(product_spec_values, [])

    def test_product_cluster_dominant_specs(self):
        dominant_specs = self.cluster.dominant_specs()
        self.assertEqual(dominant_specs[self.cat_cfg_1], {'value': 8, 'number_of_products': 2})
        self.assertEqual(dominant_specs[self.cat_cfg_2], {'value': 1400, 'number_of_products': 2})
        self.assertEqual(dominant_specs[self.cat_cfg_3], {'value': 100, 'number_of_products': 2})

        with self.subTest("empty queryset"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.none(), Product.objects.none())
            self.assertEqual(cluster.dominant_specs(), {})

    def test_product_cluster_dominant_brands(self):
        self.assertEqual(self.cluster.dominant_brands(), {'value': "whirlpool", 'number_of_products': 2})

        with self.subTest("empty queryset"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.none(), Product.objects.none())
            self.assertEqual(cluster.dominant_brands(), None)

    def test_product_cluster_average_price(self):
        self.assertEqual(self.cluster.average_price(), 361)

        with self.subTest("empty queryset"):
            cluster: ProductCluster = ProductCluster(self.category, Product.objects.none(), Product.objects.none())
            self.assertEqual(cluster.average_price(), None)
