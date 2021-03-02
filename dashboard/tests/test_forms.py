from django.test import TestCase
from model_mommy import mommy

from cms.models import Product, ProductAttribute, AttributeType, Website, Category
from dashboard.forms import CategoryTableForm


class TestForms(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.category: Category = mommy.make(Category, name="washing machines")
        cls.product: Product = mommy.make(Product, model="model_number")
        cls.attribute: AttributeType = mommy.make(AttributeType, name="test_attr", unit=None)

    def test_category_table_form__clean_axis_values(self):
        attr_1: AttributeType = mommy.make(AttributeType, name="attr_1", productattributes__data={"value": "s"})
        attr_2: AttributeType = mommy.make(AttributeType, name="attr_2", productattributes__data={"value": "s"})
        form_data: dict = dict(x_axis_values=["s"], y_axis_values=["s"], x_axis_attribute=attr_1, y_axis_attribute=attr_2,
                               category=self.category, name="test")
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
