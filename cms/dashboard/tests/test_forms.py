from django.test import TestCase
from model_mommy import mommy

from cms.dashboard.forms import CategoryTableForm, CategoryTableFilterForm
from cms.dashboard.models import CategoryTable
from cms.models import Product, AttributeType, Category


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

    def test_category_table_filter_form__search(self):
        with self.subTest("name filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, name="test")
            cat_2: CategoryTable = mommy.make(CategoryTable, name="not found")
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("query filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, query="test")
            cat_2: CategoryTable = mommy.make(CategoryTable, query="not found")
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("x_axis_values filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, x_axis_values=["test"])
            cat_2: CategoryTable = mommy.make(CategoryTable, x_axis_values=["not found"])
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("y_axis_values filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, y_axis_values=["test"])
            cat_2: CategoryTable = mommy.make(CategoryTable, y_axis_values=["not found"])
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("x_axis_attribute filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, x_axis_attribute__name="test")
            cat_2: CategoryTable = mommy.make(CategoryTable, x_axis_attribute__name="not found")
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("y_axis_attribute filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, y_axis_attribute__name="test2")
            cat_2: CategoryTable = mommy.make(CategoryTable, y_axis_attribute__name="not found2")
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("x_axis_attribute__alternate_names filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, x_axis_attribute__alternate_names=["test"])
            cat_2: CategoryTable = mommy.make(CategoryTable, x_axis_attribute__alternate_names=["not found"])
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("y_axis_attribute__alternate_names filter"):
            cat_1: CategoryTable = mommy.make(CategoryTable, y_axis_attribute__alternate_names=["test"])
            cat_2: CategoryTable = mommy.make(CategoryTable, y_axis_attribute__alternate_names=["not found"])
            form: CategoryTableFilterForm = CategoryTableFilterForm({'q': 'test'})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("category"):
            cat_1: CategoryTable = mommy.make(CategoryTable, category__name="test")
            cat_2: CategoryTable = mommy.make(CategoryTable, category__name="not found")
            form: CategoryTableFilterForm = CategoryTableFilterForm({'category': cat_1.category})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertNotIn(cat_2, tables)

        with self.subTest("attribute_type"):
            cat_1: CategoryTable = mommy.make(CategoryTable, y_axis_attribute__name="test3")
            form: CategoryTableFilterForm = CategoryTableFilterForm({'attribute_type': cat_1.y_axis_attribute})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
