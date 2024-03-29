import datetime
import statistics
from typing import Iterable

from django import forms
from django.test import TestCase
from model_mommy import mommy
from pandas import DataFrame
from pint import UndefinedUnitError

from cms.constants import MAIN, THUMBNAIL, WEEKLY, MONTHLY, YEARLY, ENERGY_LABEL_IMAGE
from cms.form_widgets import FloatInput
from cms.serializers import serializers
from cms.models import Product, ProductAttribute, WebsiteProductAttribute, json_data_default, Unit, AttributeType, \
    Website, Category, ProductImage, WebsiteProductAttributeQuerySet, EprelCategory, Brand
from cms.utils import get_dotted_path


class TestModels(TestCase):

    def test_json_data_default(self):
        self.assertEqual(json_data_default(), {"value": None})

    def test_unit(self):
        with self.subTest("text"):
            unit: Unit = mommy.make(Unit, widget=get_dotted_path(forms.widgets.TextInput))
            self.assertEqual(unit.serializer, serializers[forms.CharField])
            self.assertEqual(unit.field_class, forms.CharField)
            self.assertEqual(unit.widget_class, forms.widgets.TextInput)

        with self.subTest("int"):
            unit: Unit = mommy.make(Unit, widget=get_dotted_path(forms.widgets.NumberInput))
            self.assertEqual(unit.serializer, serializers[forms.IntegerField])
            self.assertEqual(unit.field_class, forms.IntegerField)
            self.assertEqual(unit.widget_class, forms.widgets.NumberInput)

        with self.subTest("float"):
            unit: Unit = mommy.make(Unit, widget=get_dotted_path(FloatInput))
            self.assertEqual(unit.serializer, serializers[forms.FloatField])
            self.assertEqual(unit.field_class, forms.FloatField)
            self.assertEqual(unit.widget_class, FloatInput)

        with self.subTest("bool"):
            unit: Unit = mommy.make(Unit, widget=get_dotted_path(forms.widgets.CheckboxInput))
            self.assertEqual(unit.serializer, serializers[forms.BooleanField])
            self.assertEqual(unit.field_class, forms.BooleanField)
            self.assertEqual(unit.widget_class, forms.widgets.CheckboxInput)

        with self.subTest("datetime"):
            unit: Unit = mommy.make(Unit, widget=get_dotted_path(forms.widgets.DateTimeInput))
            self.assertEqual(unit.serializer, serializers[forms.DateTimeField])
            self.assertEqual(unit.field_class, forms.DateTimeField)
            self.assertEqual(unit.widget_class, forms.widgets.DateTimeInput)

    def test_website_create_product_attribute(self):
        website: Website = mommy.make(Website)
        product: Product = mommy.make(Product)
        attribute: AttributeType = mommy.make(AttributeType, unit__widget=get_dotted_path(forms.widgets.NumberInput))
        product_attribute: WebsiteProductAttribute = website.create_product_attribute(product, attribute, "1")
        self.assertEqual(product_attribute.website, website)
        self.assertEqual(product_attribute.attribute_type, attribute)
        self.assertEqual(product_attribute.data['value'], 1)

    def test_custom_get_or_create__product(self):
        category: Category = mommy.make(Category)
        product_created: Product = Product.objects.custom_get_or_create("test_model", category)
        self.assertEqual(product_created.model, "test_model")
        self.assertEqual(product_created.category, category)

        product_retrieved: Product = Product.objects.custom_get_or_create("test_model", category)
        self.assertEqual(product_created, product_retrieved)
        self.assertEqual(Product.objects.count(), 1)

        product_created.alternate_models.append("test_model_2")
        product_created.save()
        product_retrieved: Product = Product.objects.custom_get_or_create("test_model_2", category)
        self.assertEqual(product_created, product_retrieved)
        self.assertEqual(Product.objects.count(), 1)

    def test_product_images_required(self):
        product: Product = mommy.make(Product)
        self.assertTrue(product.image_main_required)
        self.assertTrue(product.image_thumb_required)
        self.assertTrue(product.energy_label_required)
        ProductImage.objects.create(product=product, image_type=MAIN)
        ProductImage.objects.create(product=product, image_type=THUMBNAIL)
        ProductImage.objects.create(product=product, image_type=ENERGY_LABEL_IMAGE)
        product: Product = Product.objects.get(pk=product.pk)
        self.assertFalse(product.image_main_required)
        self.assertFalse(product.image_thumb_required)
        self.assertFalse(product.energy_label_required)

    def test_product_current_average_price(self):
        product: Product = mommy.make(Product)
        attribute: AttributeType = mommy.make(AttributeType, name="price")
        mommy.make(WebsiteProductAttribute, attribute_type=attribute, data={'value': 299.99}, product=product)
        mommy.make(WebsiteProductAttribute, attribute_type=attribute, data={'value': 249.99}, product=product)
        old_attrib: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type=attribute, data={'value': 99.99}, product=product)
        old_attrib.created = datetime.datetime.now() - datetime.timedelta(hours=24)
        old_attrib.save()
        self.assertEqual(product.current_average_price, str(int(statistics.mean([299.99, 249.99]))))

    def test_product_price_history(self):
        product: Product = mommy.make(Product)
        # today's prices
        price_attribute: AttributeType = mommy.make(AttributeType, name='price')
        mommy.make(WebsiteProductAttribute, product=product, data={'value': 100}, attribute_type=price_attribute)
        mommy.make(WebsiteProductAttribute, product=product, data={'value': 150}, attribute_type=price_attribute)
        # yesterday's prices
        yesterday: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=1)
        price = mommy.make(WebsiteProductAttribute, product=product, data={'value': 50}, attribute_type=price_attribute)
        price2 = mommy.make(WebsiteProductAttribute, product=product, data={'value': 100}, attribute_type=price_attribute)
        self.assertIsInstance(product.price_history(yesterday, end_date=datetime.datetime.now()), DataFrame)
        with self.subTest("daily"):
            price.created = yesterday
            price.save()
            price2.created = yesterday
            price2.save()
            price_history: dict = product.price_history(yesterday, end_date=datetime.datetime.now()).to_dict().get('price')
            self.assertEqual(price_history[datetime.datetime.now().day], 125.0)
            self.assertEqual(price_history[yesterday.day], 75)
        with self.subTest("weekly"):
            last_week: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=7)
            price.created = last_week
            price.save()
            price2.created = last_week
            price2.save()
            price_history: dict = product.price_history(last_week, end_date=datetime.datetime.now(), time_period=WEEKLY).to_dict().get('price')
            self.assertEqual(price_history[datetime.datetime.now().isocalendar()[1]], 125.0)
            self.assertEqual(price_history[last_week.isocalendar()[1]], 75)
        with self.subTest("monthly"):
            last_month: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=30)
            price.created = last_month
            price.save()
            price2.created = last_month
            price2.save()
            price_history: dict = product.price_history(last_month, end_date=datetime.datetime.now(), time_period=MONTHLY).to_dict().get('price')
            self.assertEqual(price_history[datetime.datetime.now().month], 125.0)
            self.assertEqual(price_history[last_month.month], 75)
        with self.subTest("yearly"):
            last_year: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=365)
            price.created = last_year
            price.save()
            price2.created = last_year
            price2.save()
            price_history: dict = product.price_history(last_year, end_date=datetime.datetime.now(), time_period=YEARLY).to_dict().get('price')
            self.assertEqual(price_history[datetime.datetime.now().year], 125.0)
            self.assertEqual(price_history[last_year.year], 75)

    def test_custom_get_or_create__attribute_type(self):
        unit: Unit = mommy.make(Unit)
        category: Category = mommy.make(Category)
        with self.subTest("attribute created"):
            attribute_created: AttributeType = AttributeType.objects.custom_get_or_create("test_attribute", category, unit=unit)
            self.assertEqual(attribute_created.name, "test_attribute")
            self.assertEqual(attribute_created.unit, unit)
            self.assertEqual(attribute_created.category, category)

        with self.subTest("attribute retrieved"):
            attribute_retrieved: AttributeType = AttributeType.objects.custom_get_or_create("test_attribute", category, unit)
            self.assertEqual(attribute_created, attribute_retrieved)
            self.assertEqual(AttributeType.objects.count(), 1)

        with self.subTest("attribute created for second category"):
            category2: Category = mommy.make(Category)
            new_attribute_created: AttributeType = AttributeType.objects.custom_get_or_create("test_attribute", category2, unit=unit)
            self.assertEqual(new_attribute_created.name, "test_attribute")
            self.assertEqual(new_attribute_created.unit, unit)
            self.assertEqual(new_attribute_created.category, category2)

        with self.subTest("alternate names"):
            self.assertEqual(AttributeType.objects.count(), 2)
            attribute_created.alternate_names.append("test_attribute_2")
            attribute_created.save()
            attribute_retrieved: AttributeType = AttributeType.objects.custom_get_or_create("test_attribute_2", category, unit)
            self.assertEqual(attribute_created, attribute_retrieved)
            self.assertEqual(AttributeType.objects.count(), 2)

    def test_website_product_attributes__for_last_day(self):
        attrib_1: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, website__name="site", attribute_type__name="test")
        attrib_2: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, website=attrib_1.website, attribute_type=attrib_1.attribute_type)
        attrib_2.created = datetime.datetime.now() - datetime.timedelta(hours=24)
        attrib_2.save()
        attribs: WebsiteProductAttributeQuerySet = WebsiteProductAttribute.objects.for_last_day()
        self.assertIn(attrib_1, attribs)
        self.assertNotIn(attrib_2, attribs)

    def test_website_product_attributes__for_day(self):
        attrib_1: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, website__name="site", attribute_type__name="test")
        attrib_2: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, website=attrib_1.website, attribute_type=attrib_1.attribute_type)
        attrib_2.created = datetime.datetime.now() - datetime.timedelta(hours=24)
        attrib_2.save()
        attribs: WebsiteProductAttributeQuerySet = WebsiteProductAttribute.objects.for_day(attrib_1.created.date())
        self.assertIn(attrib_1, attribs)
        self.assertNotIn(attrib_2, attribs)

    def test_custom_get_or_create__product_attribute(self):
        attribute_type: AttributeType = mommy.make(AttributeType, unit__widget=get_dotted_path(FloatInput))
        product: Product = mommy.make(Product)
        created_attribute: ProductAttribute = ProductAttribute.objects.custom_get_or_create(product, attribute_type, "299")
        self.assertEqual(created_attribute.attribute_type, attribute_type)
        self.assertEqual(created_attribute.product, product)
        self.assertEqual(created_attribute.data['value'], 299.0)

        retrieved_attribute: ProductAttribute = ProductAttribute.objects.custom_get_or_create(product, attribute_type, "299")
        self.assertEqual(retrieved_attribute, created_attribute)

    def test_product_get_eprel_api_url(self):
        category: Category = mommy.make(Category, name="washers")
        product: Product = Product.objects.create(model="EWD 71452 W UK N", category=category, eprel_code=None, eprel_scraped=False, eprel_category=None)
        with self.subTest("no code"):
            self.assertIsNone(product.get_eprel_api_url())

        with self.subTest("code added, no eprel category"):
            product.eprel_code = "298173"
            product.save()
            self.assertIsNone(product.get_eprel_api_url())

        with self.subTest("code added, eprel category"):
            eprel_category: EprelCategory = EprelCategory.objects.create(category=category, name="washingmachines2019")
            self.assertIsInstance(product.get_eprel_api_url(), dict)
            self.assertEqual("https://eprel.ec.europa.eu/api/products/washingmachines2019/298173", product.get_eprel_api_url())
            self.assertEqual(product.eprel_category, eprel_category)

        with self.subTest("eprel category added to product"):
            self.assertEqual("https://eprel.ec.europa.eu/api/products/washingmachines2019/298173", product.get_eprel_api_url())

    def test_product_attributes_serialize(self):
        attribute_type: AttributeType = mommy.make(AttributeType, name="weight", unit=mommy.make(Unit, name="kg", widget=get_dotted_path(FloatInput)))
        attr_1 = mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': '100'})
        attr_2 = mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': '200.20'})
        attrs = ProductAttribute.objects.serialize()
        self.assertEqual(attrs.get(pk=attr_1.pk).data['value'], 100.0)
        self.assertEqual(attrs.get(pk=attr_2.pk).data['value'], 200.20)
        mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 'test'})
        with self.assertRaises(UndefinedUnitError) as context:
            ProductAttribute.objects.serialize()
        self.assertEqual(str(context.exception), "'test' is not defined in the unit registry")

    def test_attribute_type_convert_unit(self):
        kilogram: Unit = mommy.make(Unit, name="kilogram", widget=get_dotted_path(FloatInput))
        attribute_type: AttributeType = mommy.make(AttributeType, name="weight", unit=kilogram)

        with self.subTest("same unit type"):
            self.assertEqual(attribute_type.convert_unit(kilogram).unit, kilogram)

        gram: Unit = mommy.make(Unit, name="gram", widget=get_dotted_path(FloatInput))
        mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 7})
        with self.subTest("convert to grams"):
            self.assertEqual(attribute_type.convert_unit(gram).unit, gram)
            self.assertTrue(ProductAttribute.objects.filter(attribute_type=attribute_type, data__value=7000))

        with self.subTest("unit is None"):
            attribute_type_1: AttributeType = mommy.make(AttributeType, unit=None)
            attribute_type_2: AttributeType = mommy.make(AttributeType, unit=None)
            self.assertIsNone(attribute_type_1.convert_unit(attribute_type_2.unit).unit)

        with self.subTest("mismatch units"):
            litre: Unit = mommy.make(Unit, name="litre", widget=get_dotted_path(FloatInput))
            mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 7})
            with self.assertRaises(Exception) as context:
                attribute_type.convert_unit(litre)
            self.assertEqual(str(context.exception), "Cannot convert from 'gram' ([mass]) to 'liter' ([length] ** 3)")
            self.assertTrue(ProductAttribute.objects.filter(attribute_type=attribute_type, attribute_type__unit=gram, data__value=7))

        with self.subTest("text conversion attempt"):
            mg: Unit = mommy.make(Unit, name="mg", widget=get_dotted_path(FloatInput))
            mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 'test'})
            with self.assertRaises(Exception) as context:
                attribute_type.convert_unit(mg)
            self.assertEqual(str(context.exception), "'test' is not defined in the unit registry")
            self.assertTrue(ProductAttribute.objects.filter(attribute_type=attribute_type, attribute_type__unit=gram, data__value='test'))

        with self.subTest("adding new unit"):
            kg: Unit = mommy.make(Unit, name="kg", widget=get_dotted_path(FloatInput))
            attribute_type: AttributeType = mommy.make(AttributeType, unit=None)
            mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': '700'})
            attribute_type.convert_unit(kg)
            self.assertEqual(AttributeType.objects.get(pk=attribute_type.pk).unit, kg)
            self.assertTrue(ProductAttribute.objects.filter(attribute_type=attribute_type, data__value=700.0))

    def test_product_update_brand(self):
        product: Product = Product.objects.create(model="test")
        with self.subTest("new brand"):
            self.assertFalse(Brand.objects.filter(name="new brand").exists())
            product: Product = product.update_brand("new brand")
            brand: Brand = Brand.objects.get(name="new brand")
            self.assertEqual(product.brand, brand)

        with self.subTest("product already has brand"):
            with self.assertRaises(Exception) as context:
                product.update_brand("new brand")
            self.assertEqual(str(context.exception), f"Product brand already exists: {brand}")

        with self.subTest("add existing brand to product"):
            product2: Product = Product.objects.create(model="test2")
            product2: Product = product2.update_brand("new brand")
            self.assertEqual(product2.brand, brand)

    def test_products_brands(self):
        brand: Brand = mommy.make(Brand)
        product: Product = Product.objects.create(model="test")
        product = product.update_brand("new brand")
        product2: Product = Product.objects.create(model="test2")
        product2 = product2.update_brand("unpub brand")
        unpub_brand = product2.brand
        unpub_brand.publish = False
        unpub_brand.save()
        self.assertIn(product.brand, Product.objects.brands())
        self.assertNotIn(brand, Product.objects.brands())
        self.assertNotIn(unpub_brand, Product.objects.brands())

    def test_category_searchable_names(self):
        category: Category = mommy.make(Category, name="washers", alternate_names=["front loaders", "frontloaders"])
        searchable_names = category.searchable_names
        self.assertIsInstance(searchable_names, Iterable)
        searchable_names = list(searchable_names)
        self.assertIn("washers", searchable_names)
        self.assertIn("front loaders", searchable_names)
