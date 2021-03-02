from django.test import TestCase
from model_mommy import mommy

from cms.models import Product, ProductAttribute, WebsiteProductAttribute, AttributeType, Website, Category
from dashboard.forms import CategoryTableForm


class TestForms(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.website: Website = mommy.make(Website, name="test_website", currency__name="€")
        cls.category: Category = mommy.make(Category, name="washing machines")
        cls.product: Product = mommy.make(Product, model="model_number")
        cls.attribute: AttributeType = mommy.make(AttributeType, name="test_attr", unit=None)
        cls.product_attribute: ProductAttribute = mommy.make(ProductAttribute, product=cls.product, attribute_type=cls.attribute)

    def test_category_table_form__values_numeric(self):
        x_axis_attribute: AttributeType = mommy.make(AttributeType, productattributes__data={"value": "s"})
        y_axis_attribute: AttributeType = mommy.make(AttributeType, productattributes__data={"value": "s"})
        with self.subTest("int"):
            form_data: dict = dict(x_axis_values=["1"], y_axis_values=["1"], x_axis_attribute=x_axis_attribute,
                                   y_axis_attribute=y_axis_attribute, category=self.category)
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
        form_data: dict = dict(x_axis_values=["s"], y_axis_values=["s"], x_axis_attribute=attr_1, y_axis_attribute=attr_2,
                               category=self.category)
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
