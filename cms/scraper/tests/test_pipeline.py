from typing import List, Dict

from django.test import TestCase
from model_mommy import mommy

from cms.constants import PRICE, MAIN, THUMBNAIL
from cms.form_widgets import FloatInput
from cms.models import Category, Product, ProductAttribute, Unit, Website, Selector, WebsiteProductAttribute, \
    AttributeType, ProductImage
from cms.utils import get_dotted_path

from cms.scraper.items import ProductPageItem
from cms.scraper.pipelines import ProductPipeline, ProductAttributePipeline, WebsiteProductAttributePipeline, \
    ProductImagePipeline


class TestPipeline(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.website: Website = mommy.make(Website, name="test_website", currency__name="€", currency__widget=get_dotted_path(FloatInput))
        cls.category: Category = mommy.make(Category, name="washing machines")
        cls.product: Product = mommy.make(Product, model="model_number", category=cls.category)

    def test_product(self):
        with self.subTest("create"):
            item: ProductPageItem = ProductPageItem()
            item['model'] = "model_number_2"
            item['category'] = self.category
            item: ProductPageItem = ProductPipeline().process_item(item, {})
            self.assertIsInstance(item, ProductPageItem)
            self.assertIsInstance(item['product'], Product)
            self.assertEqual(item['product'].model, "model_number_2")
            self.assertEqual(item['product'].category, self.category)

        with self.subTest("get"):
            item: ProductPageItem = ProductPageItem()
            item['model'] = "model_number"
            item['category'] = self.category
            item: ProductPageItem = ProductPipeline().process_item(item, {})
            self.assertIsInstance(item, ProductPageItem)
            self.assertEqual(item['product'], self.product)
            self.assertEqual(item['product'].model, "model_number")
            self.assertEqual(item['product'].category, self.category)

    def test_product_attribute(self):
        item: ProductPageItem = ProductPageItem(product=self.product, category=self.category)
        with self.subTest("unit"):
            self.assertFalse(ProductAttribute.objects.filter(product=self.product, attribute_type__name='Wash capacity').exists())
            self.assertFalse(Unit.objects.filter(name="kilogram").first())
            item['attributes']: List[Dict] = [{'value': '10kg', 'label': 'Wash capacity'}]
            ProductAttributePipeline().process_item(item, {})
            self.assertTrue(ProductAttribute.objects.filter(product=self.product, attribute_type__name='Wash capacity', data__value=10).exists())
            self.assertTrue(Unit.objects.filter(name="kilogram").first())
        with self.subTest("range unit"):
            self.assertFalse(ProductAttribute.objects.filter(product=self.product, attribute_type__name='power - low').exists())
            self.assertFalse(ProductAttribute.objects.filter(product=self.product, attribute_type__name='power - high').exists())
            self.assertFalse(Unit.objects.filter(name="volt").first())
            item['attributes']: List[Dict] = [{'value': '220 - 240v', 'label': 'power'}]
            ProductAttributePipeline().process_item(item, {})
            self.assertTrue(ProductAttribute.objects.filter(product=self.product, attribute_type__name='power - low', data__value=220).exists())
            self.assertTrue(ProductAttribute.objects.filter(product=self.product, attribute_type__name='power - high', data__value=240).exists())
            self.assertTrue(Unit.objects.filter(name="volt").first())
        with self.subTest("energy rating"):
            self.assertFalse(ProductAttribute.objects.filter(product=self.product, attribute_type__name='energy rating').exists())
            item['attributes']: List[Dict] = [{'value': 'a+++', 'label': 'energy rating'}]
            ProductAttributePipeline().process_item(item, {})
            self.assertTrue(ProductAttribute.objects.filter(product=self.product, attribute_type__name='energy rating', data__value="a+++").exists())

    def test_website_product_attribute(self):
        item: ProductPageItem = ProductPageItem(product=self.product, category=self.category, website=self.website)
        item['website_attributes']: List[Dict] = [{
            'value': '399.99',
            'selector': mommy.make(Selector, website=self.website, selector_type=PRICE)
        }, {
            'value': '499.99',
            'selector': mommy.make(Selector, website=self.website, selector_type="invalid selector")
        }]
        WebsiteProductAttributePipeline().process_item(item, {})
        attribute_type: AttributeType = AttributeType.objects.get(name="price", unit=self.website.currency)
        self.assertTrue(WebsiteProductAttribute.objects.filter(website=self.website, attribute_type=attribute_type, product=self.product, data__value=399.99).exists())
        self.assertFalse(WebsiteProductAttribute.objects.filter(website=self.website, attribute_type=attribute_type, product=self.product, data__value=499.99).exists())

    def test_product_image_pipeline(self):
        item: ProductPageItem = ProductPageItem(product=self.product, images=[{'path': 'full/testimage.jpg'}])
        ProductImagePipeline().process_item(item, {})
        self.assertTrue(ProductImage.objects.filter(product=self.product, image_type=MAIN, image='product_images/full/testimage.jpg').exists())
        self.assertTrue(ProductImage.objects.filter(product=self.product, image_type=THUMBNAIL, image='product_images/thumbs/big/testimage.jpg').exists())
        item['images'] = [{'path': 'full/testimage2.jpg'}]
        self.assertFalse(ProductImage.objects.filter(product=self.product, image_type=MAIN, image='product_images/full/testimage2.jpg').exists())
        self.assertFalse(ProductImage.objects.filter(product=self.product, image_type=THUMBNAIL, image='product_images/thumbs/big/testimage2.jpg').exists())
