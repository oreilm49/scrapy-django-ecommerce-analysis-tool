from django.test import TestCase
from model_mommy import mommy

from cms.dashboard.forms import CategoryTableForm, CategoryTableFilterForm, ProductsFilterForm
from cms.dashboard.models import CategoryTable
from cms.models import Product, AttributeType, Category, ProductAttribute, WebsiteProductAttribute, Brand


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
            cat_2: CategoryTable = mommy.make(CategoryTable, x_axis_attribute=cat_1.y_axis_attribute)
            form: CategoryTableFilterForm = CategoryTableFilterForm({'attribute_type': cat_1.y_axis_attribute})
            form.is_valid()
            tables = form.search(CategoryTable.objects.all())
            self.assertIn(cat_1, tables)
            self.assertIn(cat_2, tables)

    def test_products_filter_form(self):
        whirlpool: Brand = Brand.objects.create(name="whirlpool")
        with self.subTest("brands"):
            form: ProductsFilterForm = ProductsFilterForm()
            self.assertEqual([brand.pk for brand in form.fields['brands'].queryset], [brand.pk for brand in Brand.objects.all()])

        with self.subTest("q"):
            with self.subTest("model"):
                prod_1: Product = mommy.make(Product, model="test")
                prod_2: Product = mommy.make(Product, model="not found")
                form: ProductsFilterForm = ProductsFilterForm({'q': 'test'})
                form.is_valid()
                tables = form.search(Product.objects.all())
                self.assertIn(prod_1, tables)
                self.assertNotIn(prod_2, tables)

            with self.subTest("alternate_models"):
                prod_1: Product = mommy.make(Product, alternate_models=["test"])
                prod_2: Product = mommy.make(Product, alternate_models=["not found"])
                form: ProductsFilterForm = ProductsFilterForm({'q': 'test'})
                form.is_valid()
                tables = form.search(Product.objects.all())
                self.assertIn(prod_1, tables)
                self.assertNotIn(prod_2, tables)

            with self.subTest("category"):
                prod_1: Product = mommy.make(Product, category__name="test")
                prod_2: Product = mommy.make(Product, category__name="not found")
                form: ProductsFilterForm = ProductsFilterForm({'q': 'test'})
                form.is_valid()
                tables = form.search(Product.objects.all())
                self.assertIn(prod_1, tables)
                self.assertNotIn(prod_2, tables)

        with self.subTest("price_low"):
            price_attr: AttributeType = mommy.make(AttributeType, name="price")
            mommy.make(WebsiteProductAttribute, product=prod_1, attribute_type=price_attr, data={'value': 100})
            mommy.make(WebsiteProductAttribute, product=prod_2, attribute_type=price_attr, data={'value': 50})
            form: ProductsFilterForm = ProductsFilterForm({'price_low': 75})
            form.is_valid()
            tables = form.search(Product.objects.all())
            self.assertIn(prod_1, tables)
            self.assertNotIn(prod_2, tables)

        with self.subTest("price_high"):
            form: ProductsFilterForm = ProductsFilterForm({'price_high': 75})
            form.is_valid()
            tables = form.search(Product.objects.all())
            self.assertNotIn(prod_1, tables)
            self.assertIn(prod_2, tables)

        with self.subTest("brands"):
            form: ProductsFilterForm = ProductsFilterForm({'brands': [whirlpool]})
            form.is_valid()
            product: Product = Product.objects.create(model="test3", brand=whirlpool)
            tables = form.search(Product.objects.all())
            self.assertIn(product, tables)
            self.assertNotIn(prod_1, tables)
