from typing import List
from unittest import skip

from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from cms.accounts.models import Company
from cms.dashboard.models import CategoryTable, CategoryGapAnalysisReport
from cms.dashboard.reports import ProductCluster
from cms.models import Product, WebsiteProductAttribute, AttributeType, Category, Website, Brand
from cms.scripts.load_cms import run as load_cms


class TestModels(TestCase):

    def test_category_table_get_products(self):
        category: Category = mommy.make(Category)
        whirlpool: Brand = Brand.objects.create(name="whirlpool")
        hotpoint: Brand = Brand.objects.create(name="hotpoint")
        indesit: Brand = Brand.objects.create(name="indesit")
        product_1: Product = mommy.make(Product, category=category, model="product_1", brand=whirlpool)
        product_2: Product = mommy.make(Product, category=category, model="product_2", brand=hotpoint)
        product_3: Product = mommy.make(Product, category=category, model="product_3", brand=indesit)
        product_4: Product = mommy.make(Product, category__name="dryers", model="product_4", brand=hotpoint)
        product_5: Product = mommy.make(Product, category=category, model="filtered_by_search", brand=hotpoint)
        brand_attr: AttributeType = mommy.make(AttributeType, name="brand")
        price_attr: WebsiteProductAttribute = mommy.make(WebsiteProductAttribute, attribute_type__name="price")
        mommy.make(WebsiteProductAttribute, product=product_1, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 150})
        mommy.make(WebsiteProductAttribute, product=product_2, attribute_type=price_attr.attribute_type, data={'value': 40})
        mommy.make(WebsiteProductAttribute, product=product_3, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 250})
        mommy.make(WebsiteProductAttribute, product=product_4, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 150})
        mommy.make(WebsiteProductAttribute, product=product_5, attribute_type=price_attr.attribute_type, website=price_attr.website, data={'value': 150})
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
            products = table.get_products
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
            products = table.get_products
            self.assertIn(product_1, products)
            self.assertNotIn(product_2, products)

        with self.subTest("brands filter"):
            table.brands.add(hotpoint)
            table.websites.remove(price_attr.website)
            table.save()
            products = table.get_products
            self.assertNotIn(product_1, products)
            self.assertIn(product_2, products)

        with self.subTest("products filter"):
            product_4.category = category
            product_4.save()
            table.products.add(product_4)
            table.save()
            products = table.get_products
            self.assertNotIn(product_2, products)
            self.assertIn(product_4, products)

        with self.subTest("price filter"):
            table.products.remove(product_4)
            table.brands.remove(hotpoint)
            table.price_low = 100
            table.price_high = 200
            table.save()
            products = table.get_products
            self.assertIn(product_1, products)
            self.assertNotIn(product_2, products)
            self.assertNotIn(product_3, products)

    @skip("algorithm not perfected yet")
    def test_category_table_build_table(self):
        load_cms()
        table: CategoryTable = mommy.make(
            CategoryTable,
            x_axis_values=[0, 199, 299],
            y_axis_values=["indesit", "beko", "candy"],
            x_axis_attribute=AttributeType.objects.get(name="price"),
            y_axis_attribute=AttributeType.objects.get(name="brand"),
            category=Category.objects.get(name="washing machines"),
            name="test",
        )
        table_dict: dict = table.build_table(Product.objects.all())
        self.assertEqual(len(table_dict['indesit']), len(table_dict['beko']))
        self.assertEqual(len(table_dict['candy']), len(table_dict['beko']))

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
        whirlpool: Brand = Brand.objects.create(name="whirlpool")
        bosch: Brand = Brand.objects.create(name="bosch")
        report: CategoryGapAnalysisReport = mommy.make(CategoryGapAnalysisReport, category__name="washers", brand=whirlpool)
        product = mommy.make(Product, brand=whirlpool, category=report.category)
        product2 = mommy.make(Product, brand=bosch, category=report.category)
        with self.subTest("products"):
            self.assertIn(product, report.products)
            self.assertIn(product2, report.products)
        with self.subTest("target range"):
            self.assertIn(product, report.target_range)
            self.assertNotIn(product2, report.target_range)
