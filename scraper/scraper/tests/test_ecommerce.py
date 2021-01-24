from collections import Iterator

import scrapy
from betamax import Betamax
from betamax.fixtures.unittest import BetamaxTestCase
from model_mommy import mommy
from requests import Response
from scrapy.http import HtmlResponse

from cms.models import Website, Url, Category
from cms.constants import CATEGORY
from scraper.spiders.ecommerce import EcommerceSpider


with Betamax.configure() as config:
    config.cassette_library_dir = 'cassettes'
    config.preserve_exact_body_bytes = True


class TestEcommerce(BetamaxTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.website: Website = mommy.make(Website, name="harvey norman", domain="harveynorman.ie")
        cls.category: Category = mommy.make(Category, name="Washing Machines")
        cls.url: Url = mommy.make(Url, url="https://www.harveynorman.ie/home-appliances/appliances/washing-machines/", url_type=CATEGORY, website=cls.website, category=cls.category)

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
        pass
