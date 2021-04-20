import itertools

from django.test import TestCase
from model_mommy import mommy

from cms.models import Product, ProductAttribute, WebsiteProductAttribute, AttributeType, Brand
from cms.utils import products_grouper, extract_grouper, filename_from_path, migrate_brands_delete_attrs


class TestUtils(TestCase):

    def test_extract_grouper(self):
        self.assertEqual(extract_grouper("hello", ["hello", "world"]), "hello")
        self.assertIsNone(extract_grouper("goodbye", ["hello", "world"]))
        self.assertEqual(extract_grouper(159, [0, 99, 199, 299]), 199)
        self.assertEqual(extract_grouper(159, [299, 99, 199, 299]), 299)

    def test_products_grouper(self):
        product: Product = mommy.make(Product)
        with self.subTest("product attributes"):
            product_attribute: ProductAttribute = mommy.make(ProductAttribute, attribute_type__name="brand", data={"value": "whirlpool"}, product=product)
            self.assertEqual(products_grouper(product, product_attribute.attribute_type, ["whirlpool", "hotpoint"]), "whirlpool")
            self.assertEqual(products_grouper(product, product_attribute.attribute_type, ["hotpoint"]), None)

        with self.subTest("website product attributes"):
            website_attribute: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type__name="price", data={"value": 199}, product=product)
            self.assertEqual(products_grouper(product, website_attribute.attribute_type, [0, 99, 199, 299]), 199)

        with self.subTest("for queryset"):
            groups = itertools.groupby(Product.objects.iterator(), key=lambda product: products_grouper(
                product,
                website_attribute.attribute_type,
                [0, 99, 199, 299]
            ))
            self.assertEqual(list(groups)[0][0], 199)

    def test_filename_from_path(self):
        path = "opt/project/cms/media/product_images/energy_labels/9d08fa81-ba1f-4c3c-9803-cbca5a2ed010.png"
        self.assertEqual("9d08fa81-ba1f-4c3c-9803-cbca5a2ed010.png", filename_from_path(path))
