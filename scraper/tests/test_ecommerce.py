from collections import Iterator
import os
import scrapy
from betamax import Betamax
from betamax.fixtures.unittest import BetamaxTestCase
from django.test import TestCase
from model_mommy import mommy
from requests import Response
from scrapy.http import HtmlResponse

from cms.models import Website, Url, Category, PageDataItem, Selector
from cms.constants import CATEGORY, STRING, TABLE, TABLE_LABEL_COLUMN, TABLE_VALUE_COLUMN, FLOAT, TEXT
from items import ProductPageItem
from scraper.spiders.ecommerce import EcommerceSpider


with Betamax.configure() as config:
    config.cassette_library_dir = os.path.join(os.path.dirname(__file__), 'cassettes')
    config.preserve_exact_body_bytes = True


class TestEcommerce(BetamaxTestCase, TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        print(Website.objects.all())
        cls.website: Website = mommy.make(Website, name="harvey norman", domain="harveynorman.ie")
        cls.category: Category = mommy.make(Category, name="Washing Machines")
        cls.url: Url = mommy.make(Url, url="https://www.harveynorman.ie/home-appliances/appliances/washing-machines/", url_type=CATEGORY, website=cls.website, category=cls.category)
        cls.product_url: str = cls.url.url + "/whirlpool-8kg-freestanding-washing-machine-ffb8448wvuk.html"
        # Set up selectors
        table_selector: Selector = mommy.make(Selector, selector_type=TABLE, css_selector="#content_features table.table-product-features tr", website=self.website)
        mommy.make(Selector, selector_type=TABLE_LABEL_COLUMN, css_selector="th", website=cls.website, parent=table_selector)
        mommy.make(Selector, selector_type=TABLE_VALUE_COLUMN, css_selector="td", website=cls.website, parent=table_selector)
        mommy.make(PageDataItem, name="table", data_type=STRING, website=cls.website, selector=table_selector)
        mommy.make(PageDataItem, name="price", data_type=FLOAT, website=cls.website, selector=mommy.make(
            Selector, selector_type=TEXT, css_selector=".price-num", website=cls.website
        ))
        mommy.make(PageDataItem, name="model", data_type=STRING, website=cls.website, selector=mommy.make(
            Selector, selector_type=TEXT, css_selector=".product-id.meta", website=cls.website
        ))

    def test_init_spider(self):
        spider: EcommerceSpider = EcommerceSpider(website=self.website.name)
        self.assertEqual(spider.website, self.website)
        self.assertEqual(spider.allowed_domains, [self.website.domain])

    def test_start_requests(self):
        spider: EcommerceSpider = EcommerceSpider(website="harvey norman")
        requests = spider.start_requests()
        self.assertIsInstance(requests, Iterator)
        request = next(requests)
        self.assertIsInstance(next(requests), scrapy.Request)
        self.assertEqual(request.callback, spider.parse)
        self.assertEqual(request.cb_kwargs, {'category': self.category})

    def test_parse_pagination(self):
        response: Response = self.session.get(self.url.url)
        scrapy_response: HtmlResponse = HtmlResponse(body=response.content, url=self.url.url)
        spider: EcommerceSpider = EcommerceSpider(website="harvey norman")
        pages = spider.parse_pagination(scrapy_response, category=self.url.category)
        self.assertIsInstance(pages, Iterator)
        page = next(pages)
        self.assertIsInstance(page, scrapy.Request)
        self.assertEqual(page.callback, spider.parse_products)
        self.assertEqual(page.cb_kwargs, {'category': self.url.category})

    def test_parse_products(self):
        response: Response = self.session.get(self.url.url)
        scrapy_response: HtmlResponse = HtmlResponse(body=response.content, url=self.url.url)
        spider: EcommerceSpider = EcommerceSpider(website="harvey norman")
        products = spider.parse_products(scrapy_response, category=self.url.category)
        self.assertIsInstance(products, Iterator)
        product = next(products)
        self.assertIsInstance(product, scrapy.Request)
        self.assertEqual(product.callback, spider.parse_product)
        self.assertEqual(product.cb_kwargs, {'category': self.url.category})

    def test_parse_product(self):
        response: Response = self.session.get(self.product_url)
        scrapy_response: HtmlResponse = HtmlResponse(body=response.content, url=self.product_url)
        spider: EcommerceSpider = EcommerceSpider(website="harvey norman")
        product_item: ProductPageItem = next(spider.parse_product(scrapy_response, category=self.url.category))
        self.assertIsNotNone(product_item.get('model'))
        self.assertIsNotNone(product_item.get('category'))
        self.assertIsInstance(product_item['attributes'], list)
        self.assertTrue(len(product_item['attributes']) > 0)
        attribute: dict = product_item['attributes'][0]
        self.assertIsInstance(attribute, dict)
        self.assertIsInstance(attribute['data_type'], PageDataItem)
        self.assertIsInstance(attribute['value'], str)
