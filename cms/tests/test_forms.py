from django.test import TestCase
from model_mommy import mommy

from cms.constants import MAIN, THUMBNAIL
from cms.models import Category, Product, ProductAttribute, Website, WebsiteProductAttribute, AttributeType,\
    ProductImage
from cms.forms import ProductMergeForm, AttributeTypeMergeForm, CategoryTableForm


class TestForms(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.website: Website = mommy.make(Website, name="test_website", currency__name="€")
        cls.category: Category = mommy.make(Category, name="washing machines")
        cls.product: Product = mommy.make(Product, model="model_number")
        cls.attribute: AttributeType = mommy.make(AttributeType, name="test_attr", unit=None)
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

    def test_attribute_type_merge_form(self):
        duplicate: AttributeType = mommy.make(AttributeType, name="duplicate attr", unit__name="test unit", alternate_names=["test alternate name"])
        product_attr__deleted: ProductAttribute = mommy.make(ProductAttribute, product=self.product, attribute_type=duplicate)
        product_attr__mapped: ProductAttribute = mommy.make(ProductAttribute, attribute_type=duplicate)
        web_attr__mapped: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, product=self.product, attribute_type=duplicate)

        form: AttributeTypeMergeForm = AttributeTypeMergeForm(dict(duplicates=[self.attribute.pk, duplicate.pk], target=self.attribute))
        self.assertFalse(form.is_valid())
        form: AttributeTypeMergeForm = AttributeTypeMergeForm(dict(duplicates=[duplicate.pk], target=self.attribute))
        self.assertTrue(form.is_valid(), msg=form.errors)
        form.save()

        self.assertFalse(ProductAttribute.objects.filter(pk=product_attr__deleted.pk).exists())
        self.assertEqual(ProductAttribute.objects.get(pk=product_attr__mapped.pk).attribute_type, self.attribute)
        self.assertIsNotNone(AttributeType.objects.get(pk=self.attribute.pk).unit)
        self.assertEqual(WebsiteProductAttribute.objects.get(pk=web_attr__mapped.pk).attribute_type, self.attribute)

    def test_category_table_form__values_numeric(self):
        x_axis_attribute: AttributeType = mommy.make(AttributeType, productattributes__data={"value": "s"})
        y_axis_attribute: AttributeType = mommy.make(AttributeType, productattributes__data={"value": "s"})
        with self.subTest("int"):
            form_data: dict = dict(x_axis_values=["1"], y_axis_values=["1"], x_axis_attribute=x_axis_attribute, y_axis_attribute=y_axis_attribute, category=self.category)
            form: CategoryTableForm = CategoryTableForm(form_data)
            self.assertTrue(form.is_valid(), msg=form.errors)
            self.assertTrue(form.is_x_axis_values_numeric)
            self.assertTrue(form.is_y_axis_values_numeric)

        with self.subTest("float"):
            form_data.update(x_axis_values=["1.0"], y_axis_values=["1.0"])
            form: CategoryTableForm = CategoryTableForm(form_data)
            self.assertTrue(form.is_valid(), msg=form.errors)
            self.assertTrue(form.is_x_axis_values_numeric)
            self.assertTrue(form.is_y_axis_values_numeric)

        with self.subTest("str"):
            form_data.update(x_axis_values=["s"], y_axis_values=["s"])
            form: CategoryTableForm = CategoryTableForm(form_data)
            self.assertTrue(form.is_valid(), msg=form.errors)
            self.assertFalse(form.is_x_axis_values_numeric)
            self.assertFalse(form.is_y_axis_values_numeric)

    def test_category_table_form__clean_axis_values(self):
        attr_1: AttributeType = mommy.make(AttributeType, name="attr_1", productattributes__data={"value": "s"})
        attr_2: AttributeType = mommy.make(AttributeType, name="attr_2", productattributes__data={"value": "s"})
        form_data: dict = dict(x_axis_values=["s"], y_axis_values=["s"], x_axis_attribute=attr_1, y_axis_attribute=attr_2, category=self.category)
        with self.subTest("valid values"):
            form: CategoryTableForm = CategoryTableForm(form_data)
            self.assertTrue(form.is_valid(), msg=form.errors)

        with self.subTest("x axis invalid"):
            form_data.update(x_axis_values=["doesn't exist"])
            form: CategoryTableForm = CategoryTableForm(form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("'attr_1' with value 'doesn't exist' does not exist.", form.errors['x_axis_values'])

        with self.subTest("y axis invalid"):
            form_data.update(x_axis_values=["s"], y_axis_values=["doesn't exist"])
            form: CategoryTableForm = CategoryTableForm(form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("'attr_2' with value 'doesn't exist' does not exist.", form.errors['y_axis_values'])

    def test_category_table_form__search(self):
        """
        create three product attributes
        create a product for each attribute, and an attribute type
        """
        product_1: Product = mommy.make(Product, category=self.category, model="product_1")
        product_2: Product = mommy.make(Product, category=self.category, model="product_2")
        product_3: Product = mommy.make(Product, category=self.category, model="product_3")
        product_4: Product = mommy.make(Product, category__name="dryers", model="product_4")
        product_5: Product = mommy.make(Product, category=self.category, model="filtered_by_search")
        brand_attr: AttributeType = mommy.make(AttributeType, name="brand")
        price_attr: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type__name="price")
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_1, data={"value": "whirlpool"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_2, data={"value": "hotpoint"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_3, data={"value": "indesit"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_4, data={"value": "hotpoint"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_5, data={"value": "hotpoint"})
        form: CategoryTableForm = CategoryTableForm(dict(
            x_axis_values=["0", "199", "299", "399", "499"],
            y_axis_values=["whirlpool", "hotpoint"],
            x_axis_attribute=price_attr.attribute_type,
            y_axis_attribute=brand_attr,
            category=self.category,
            q="product_",
        ))
        self.assertTrue(form.is_valid(), msg=form.errors)
        products = form.search(Product.objects.published())
        self.assertIn(product_1, products)
        self.assertIn(product_2, products)
        self.assertNotIn(product_3, products)
        self.assertNotIn(product_4, products)
        self.assertNotIn(product_5, products)
