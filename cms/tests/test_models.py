import datetime
import statistics

from django import forms
from django.test import TestCase
from model_mommy import mommy
from pandas import DataFrame

from cms.constants import MAIN, THUMBNAIL, WEEKLY, MONTHLY, YEARLY, ENERGY_LABEL_IMAGE
from cms.form_widgets import FloatInput
from cms.serializers import serializers
from cms.models import Product, ProductAttribute, WebsiteProductAttribute, json_data_default, Unit, AttributeType, \
    Website, Category, ProductImage, WebsiteProductAttributeQuerySet, EprelCategory
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

    def test_product_brand(self):
        product: Product = mommy.make(Product)
        product_attribute: ProductAttribute = mommy.make(ProductAttribute, product=product, attribute_type__name="brand")
        product_attribute.data['value'] = "whirlpool"
        product_attribute.save()
        self.assertEqual(product.brand, "whirlpool")

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
        attribute_created: AttributeType = AttributeType.objects.custom_get_or_create("test_attribute", unit)
        self.assertEqual(attribute_created.name, "test_attribute")
        self.assertEqual(attribute_created.unit, unit)

        attribute_retrieved: AttributeType = AttributeType.objects.custom_get_or_create("test_attribute", unit)
        self.assertEqual(attribute_created, attribute_retrieved)
        self.assertEqual(AttributeType.objects.count(), 1)

        attribute_created.alternate_names.append("test_attribute_2")
        attribute_created.save()
        attribute_retrieved: AttributeType = AttributeType.objects.custom_get_or_create("test_attribute_2", unit)
        self.assertEqual(attribute_created, attribute_retrieved)
        self.assertEqual(AttributeType.objects.count(), 1)

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

    def test_product_queryset_brands(self):
        attribute_type: AttributeType = mommy.make(AttributeType, name="brand")
        mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 'whirlpool'})
        mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 'whirlpool'})
        mommy.make(ProductAttribute, attribute_type=attribute_type, data={'value': 'hotpoint'})
        self.assertEqual(sorted(list(Product.objects.brands())), ['hotpoint', 'whirlpool'])

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
        with self.assertRaises(ValueError) as context:
            ProductAttribute.objects.serialize()
        self.assertEqual(str(context.exception), "could not convert string to float: 'test'")
