from django.test import TestCase
from model_mommy import mommy

from cms.constants import MAIN, THUMBNAIL
from cms.models import Category, Product, ProductAttribute, Website, WebsiteProductAttribute, AttributeType, \
    ProductImage, Unit
from cms.forms import ProductMergeForm, AttributeTypeMergeForm, AttributeTypeForm


class TestForms(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.website: Website = mommy.make(Website, name="test_website", currency__name="€")
        cls.category: Category = mommy.make(Category, name="washing machines")
        cls.product: Product = mommy.make(Product, model="model_number")
        cls.gram: Unit = mommy.make(Unit, name="gram")
        cls.attribute: AttributeType = mommy.make(AttributeType, name="test_attr", unit=cls.gram)
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
        duplicate: AttributeType = mommy.make(AttributeType, name="duplicate attr", unit__name="kg", alternate_names=["test alternate name"])
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

    def test_attribute_type_form__unit_conversion(self):
        kilogram: Unit = mommy.make(Unit, name="kilogram")
        attribute_type: AttributeType = mommy.make(AttributeType, name="weight", unit=kilogram)
        form: AttributeTypeForm = AttributeTypeForm(data={'name': 'weight', 'unit': kilogram, 'alternate_names': []}, instance=attribute_type)

        with self.subTest("same unit type"):
            self.assertTrue(form.is_valid(), msg=form.errors)
            form.save()
            self.assertEqual(AttributeType.objects.get(pk=attribute_type.pk).unit, kilogram)

        mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 7})
        with self.subTest("convert to grams"):
            form: AttributeTypeForm = AttributeTypeForm({'name': 'weight', 'unit': self.gram, 'alternate_names': []}, instance=attribute_type)
            self.assertTrue(form.is_valid(), msg=form.errors)
            form.save()
            self.assertEqual(AttributeType.objects.get(pk=attribute_type.pk).unit, self.gram)
            self.assertTrue(ProductAttribute.objects.filter(attribute_type=attribute_type, data__value=7000))

        with self.subTest("unit is None"):
            attribute_type_1: AttributeType = mommy.make(AttributeType, name="test1", unit=None)
            attribute_type_2: AttributeType = mommy.make(AttributeType, name="test2", unit=None)
            form: AttributeTypeForm = AttributeTypeForm({'name': 'test1', 'unit': attribute_type_2.unit}, instance=attribute_type_1)
            self.assertTrue(form.is_valid(), msg=form.errors)
            form.save()
            self.assertIsNone(AttributeType.objects.get(pk=attribute_type_1.pk).unit)

        with self.subTest("mismatch units"):
            litre: Unit = mommy.make(Unit, name="litre")
            mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 7})
            form: AttributeTypeForm = AttributeTypeForm({'name': 'weight', 'unit': litre}, instance=attribute_type)
            self.assertFalse(form.is_valid())
            self.assertIn("Cannot convert from 'gram' ([mass]) to 'liter' ([length] ** 3)", form.errors['unit'])
            self.assertTrue(ProductAttribute.objects.filter(attribute_type=attribute_type, attribute_type__unit=self.gram, data__value=7))

        with self.subTest("text conversion attempt"):
            mg: Unit = mommy.make(Unit, name="mg")
            mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 'test'})
            form: AttributeTypeForm = AttributeTypeForm({'name': 'weight', 'unit': mg}, instance=attribute_type)
            self.assertTrue(form.is_valid(), msg=form.errors)
            with self.assertRaises(Exception) as context:
                form.save()
            self.assertIn("'test' is not defined in the unit registry", str(context.exception))
            self.assertTrue(ProductAttribute.objects.filter(attribute_type=attribute_type, attribute_type__unit=self.gram, data__value='test'))
