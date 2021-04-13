from typing import List

from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from cms.accounts.models import Company
from cms.dashboard.models import CategoryTable, CategoryGapAnalysisReport
from cms.dashboard.reports import ProductCluster
from cms.models import Product, ProductAttribute, WebsiteProductAttribute, AttributeType, Category, Website


class TestModels(TestCase):

    def test_category_table_get_products(self):
        category: Category = mommy.make(Category)
        product_1: Product = mommy.make(Product, category=category, model="product_1")
        product_2: Product = mommy.make(Product, category=category, model="product_2")
        product_3: Product = mommy.make(Product, category=category, model="product_3")
        product_4: Product = mommy.make(Product, category__name="dryers", model="product_4")
        product_5: Product = mommy.make(Product, category=category, model="filtered_by_search")
        brand_attr: AttributeType = mommy.make(AttributeType, name="brand")
        price_attr: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type__name="price")
        mommy.make(WebsiteProductAttribute, product=product_1, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 150})
        mommy.make(WebsiteProductAttribute, product=product_2, attribute_type=price_attr.attribute_type, data={'value': 40})
        mommy.make(WebsiteProductAttribute, product=product_3, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 250})
        mommy.make(WebsiteProductAttribute, product=product_4, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 150})
        mommy.make(WebsiteProductAttribute, product=product_5, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 150})
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
        with self.subTest("attribute filtering"):
            products = table.get_products(Product.objects.published())
            self.assertIn(product_1, products)
            self.assertIn(product_2, products)
            self.assertNotIn(product_3, products)
            self.assertNotIn(product_4, products)
            self.assertNotIn(product_5, products)

        table.x_axis_values = []
        table.y_axis_values = []
        table.save()

        with self.subTest("websites filter"):
            table.websites.add(price_attr.website)
            products = table.get_products(Product.objects.published())
            self.assertIn(product_1, products)
            self.assertNotIn(product_2, products)

        with self.subTest("brands filter"):
            table.brands = ["hotpoint"]
            table.websites.remove(price_attr.website)
            table.save()
            products = table.get_products(Product.objects.published())
            self.assertNotIn(product_1, products)
            self.assertIn(product_2, products)

        with self.subTest("products filter"):
            product_4.category = category
            product_4.save()
            table.products.add(product_4)
            table.save()
            products = table.get_products(Product.objects.published())
            self.assertNotIn(product_2, products)
            self.assertIn(product_4, products)

        with self.subTest("price filter"):
            table.products.remove(product_4)
            table.brands = []
            table.price_low = 100
            table.price_high = 200
            table.save()
            products = table.get_products(Product.objects.published())
            self.assertIn(product_1, products)
            self.assertNotIn(product_2, products)
            self.assertNotIn(product_3, products)

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

    def test_gap_analysis_get_products(self):
        website: Website = mommy.make(Website)
        report: CategoryGapAnalysisReport = mommy.make(CategoryGapAnalysisReport, category__name="washers", websites=[website])
        price_attr: AttributeType = mommy.make(AttributeType, name="price")
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 200})
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 150})
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 100})
        mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 50})
        different_category: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, website=website, data={'value': 50})
        different_site: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, data={'value': 50})
        products: List[Product] = report.get_products()
        self.assertEqual(products[0].current_average_price, '50')
        self.assertEqual(products[1].current_average_price, '100')
        self.assertEqual(products[2].current_average_price, '150')
        self.assertEqual(products[3].current_average_price, '200')
        self.assertNotIn(different_category, products)
        self.assertNotIn(different_site, products)

    def test_cluster_analysis(self):
        website: Website = mommy.make(Website)
        report: CategoryGapAnalysisReport = mommy.make(CategoryGapAnalysisReport, category__name="washers", websites=[website], price_clusters=[99.99, 149.99, 199.99, 249.99])
        price_attr: AttributeType = mommy.make(AttributeType, name="price")
        p1 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 99})
        p2 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 149})
        p3 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 199})
        p4 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 249})
        with self.subTest("cluster products"):
            for grouper, group in report.cluster_products():
                if grouper == 99.99:
                    self.assertTrue(p1.product in group)
                elif grouper == 149.99:
                    self.assertTrue(p2.product in group)
                elif grouper == 199.99:
                    self.assertTrue(p3.product in group)
                elif grouper == 249.99:
                    self.assertTrue(p4.product in group)
        with self.subTest("cluster analysis"):
            analyzed_clusters: List[ProductCluster] = report.gap_analysis_clusters
            self.assertIsInstance(analyzed_clusters[0], ProductCluster)

    def test_gap_analysis_products(self):
        report: CategoryGapAnalysisReport = mommy.make(CategoryGapAnalysisReport, category__name="washers", brand="whirlpool")
        brand_attr: AttributeType = mommy.make(AttributeType, name="brand")
        p1 = mommy.make(ProductAttribute, attribute_type=brand_attr, product__category=report.category, data={'value': "whirlpool"})
        p2 = mommy.make(ProductAttribute, attribute_type=brand_attr, product__category=report.category, data={'value': "bosch"})
        with self.subTest("products"):
            self.assertIn(p1.product, report.products)
            self.assertIn(p1.product, report.products)
        with self.subTest("target range"):
            self.assertIn(p1.product, report.target_range)
            self.assertNotIn(p2.product, report.target_range)
