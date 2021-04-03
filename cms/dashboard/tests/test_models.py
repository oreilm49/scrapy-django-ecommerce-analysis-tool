from typing import List

from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from cms.accounts.models import Company
from cms.dashboard.models import CategoryTable, CategoryGapAnalysisReport
from cms.dashboard.reports import ProductCluster
from cms.models import Product, ProductAttribute, WebsiteProductAttribute, AttributeType, Category, Website


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
        report: CategoryGapAnalysisReport = mommy.make(CategoryGapAnalysisReport, category__name="washers", websites=[website])
        price_attr: AttributeType = mommy.make(AttributeType, name="price")
        p1 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 200})
        p2 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 210})
        p3 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 150})
        p4 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 140})
        p5 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 100})
        p6 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 110})
        p7 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 50})
        p8 = mommy.make(WebsiteProductAttribute, attribute_type=price_attr, product__category=report.category, website=website, data={'value': 40})
        with self.subTest("cluster products"):
            groups: List[List[Product]] = report.cluster_products()
            self.assertIn(p8.product, groups[0])
            self.assertIn(p7.product, groups[0])
            self.assertIn(p6.product, groups[1])
            self.assertIn(p5.product, groups[1])
            self.assertIn(p4.product, groups[2])
            self.assertIn(p3.product, groups[2])
            self.assertIn(p2.product, groups[3])
            self.assertIn(p1.product, groups[3])
        with self.subTest("cluster analysis"):
            analyzed_clusters: List[ProductCluster] = report.gap_analysis_clusters()
            self.assertIsInstance(analyzed_clusters[0], ProductCluster)
            self.assertEqual(len(analyzed_clusters), len(groups))

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
