from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from cms.accounts.models import Company
from cms.dashboard.models import CategoryTable
from cms.models import Product, ProductAttribute, WebsiteProductAttribute, AttributeType, Category


class TestModels(TestCase):

    def test_category_table_products(self):
        category: Category = mommy.make(Category)
        product_1: Product = mommy.make(Product, category=category, model="product_1")
        product_2: Product = mommy.make(Product, category=category, model="product_2")
        product_3: Product = mommy.make(Product, category=category, model="product_3")
        product_4: Product = mommy.make(Product, category__name="dryers", model="product_4")
        product_5: Product = mommy.make(Product, category=category, model="filtered_by_search")
        brand_attr: AttributeType = mommy.make(AttributeType, name="brand")
        price_attr: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type__name="price")
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_1, data={"value": "whirlpool"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_2, data={"value": "hotpoint"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_3, data={"value": "indesit"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_4, data={"value": "hotpoint"})
        mommy.make(ProductAttribute, attribute_type=brand_attr, product=product_5, data={"value": "hotpoint"})
        table: CategoryTable = mommy.make(
            CategoryTable,
            x_axis_values=["0", "199", "299", "399", "499"],
            y_axis_values=["whirlpool", "hotpoint"],
            x_axis_attribute=price_attr.attribute_type,
            y_axis_attribute=brand_attr,
            category=category,
            query="product_",
            name="test",
        )
        products = table.products(Product.objects.published())
        self.assertIn(product_1, products)
        self.assertIn(product_2, products)
        self.assertNotIn(product_3, products)
        self.assertNotIn(product_4, products)
        self.assertNotIn(product_5, products)

    def test_category_table_for_user(self):
        company: Company = mommy.make(Company, name="test company")
        user: User = mommy.make(User)
        user.profile.company = company
        user.save()
        owned_table: CategoryTable = mommy.make(CategoryTable, user=user)

        colleague: User = mommy.make(User)
        colleague.profile.company = company
        colleague.save()
        colleagues_table: CategoryTable = mommy.make(CategoryTable, user=colleague)
        unowned_table: CategoryTable = mommy.make(CategoryTable)
        tables = CategoryTable.objects.for_user(user)
        self.assertIn(owned_table, tables)
        self.assertIn(colleagues_table, tables)
        self.assertNotIn(unowned_table, tables)
