import itertools

from django.test import TestCase
from model_mommy import mommy

from cms.models import Product, WebsiteProductAttribute, AttributeType, Category, EprelCategory
from cms.utils import products_grouper, extract_grouper, filename_from_path, get_eprel_api_url_and_category


class TestUtils(TestCase):

    def test_extract_grouper(self):
        self.assertEqual(extract_grouper("hello", ["hello", "world"]), "hello")
        self.assertIsNone(extract_grouper("goodbye", ["hello", "world"]))
        self.assertEqual(extract_grouper(159, [0, 99, 199, 299]), 199)
        self.assertEqual(extract_grouper(159, [299, 99, 199, 299]), 299)

    def test_products_grouper(self):
        product: Product = mommy.make(Product, brand__name="whirlpool")
        with self.subTest("product attributes"):
            attribute: AttributeType = mommy.make(AttributeType, name="brand")
            self.assertEqual(products_grouper(product, attribute, ["whirlpool", "hotpoint"]), "whirlpool")
            self.assertEqual(products_grouper(product, attribute, ["hotpoint"]), None)

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

    def test_get_eprel_api_url_and_category(self):
        category: Category = mommy.make(Category, name="washing machines")
        with self.subTest("no eprel categories"):
            self.assertIsNone(get_eprel_api_url_and_category("test", category))

        with self.subTest("wrong eprel category name"):
            mommy.make(EprelCategory, name="washingmachines", category=category)
            self.assertIsNone(get_eprel_api_url_and_category("258076", category))

        with self.subTest("eprel category exists"):
            eprel_cat: EprelCategory = mommy.make(EprelCategory, name="washingmachines2019", category=category)
            eprel_cat_and_url = get_eprel_api_url_and_category("258076", category)
            self.assertIsInstance(eprel_cat_and_url, tuple)
            self.assertEqual(eprel_cat_and_url[0], eprel_cat)
            self.assertEqual(eprel_cat_and_url[1], "https://eprel.ec.europa.eu/api/products/washingmachines2019/258076")
            self.assertIsInstance(eprel_cat_and_url[2], dict)
