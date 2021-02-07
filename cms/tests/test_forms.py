from django.test import TestCase
from model_mommy import mommy

from cms.constants import MAIN, THUMBNAIL
from cms.models import Category, Product, ProductAttribute, Website, WebsiteProductAttribute, AttributeType,\
    ProductImage
from cms.forms import ProductMergeForm


class TestForms(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.website: Website = mommy.make(Website, name="test_website", currency__name="€")
        cls.category: Category = mommy.make(Category, name="washing machines")
        cls.product: Product = mommy.make(Product, model="model_number")
        cls.attribute: AttributeType = mommy.make(AttributeType, name="test_attr")
        cls.product_attribute: ProductAttribute = mommy.make(ProductAttribute, product=cls.product, attribute_type=cls.attribute)

    def test_product_merge_form(self):
        dup_product: Product = mommy.make(Product, model="duplicate", category=self.category)
        prod_attr_missing: ProductAttribute = mommy.make(ProductAttribute, product=dup_product)
        prod_attr: ProductAttribute = mommy.make(ProductAttribute, product=dup_product, attribute_type=self.attribute)
        prod_web_attr: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, product=dup_product)
        main_image: ProductImage = ProductImage.objects.create(product=dup_product, image_type=MAIN)
        thumb_image: ProductImage = ProductImage.objects.create(product=dup_product, image_type=THUMBNAIL)

        form: ProductMergeForm = ProductMergeForm(dict(duplicates=[self.product.pk, dup_product.pk], target=self.product))
        self.assertFalse(form.is_valid())
        form: ProductMergeForm = ProductMergeForm(dict(duplicates=[dup_product.pk], target=self.product))
        self.assertTrue(form.is_valid(), msg=form.errors)
        form.save()

        self.assertFalse(Product.objects.filter(pk=dup_product.pk).exists())
        self.assertFalse(ProductAttribute.objects.filter(pk=prod_attr.pk).exists())

        self.assertEqual(ProductAttribute.objects.get(pk=prod_attr_missing.pk).product, self.product)
        self.assertEqual(WebsiteProductAttribute.objects.get(pk=prod_web_attr.pk).product, self.product)
        self.assertEqual(ProductImage.objects.get(pk=main_image.pk).product, self.product)
        self.assertEqual(ProductImage.objects.get(pk=thumb_image.pk).product, self.product)
