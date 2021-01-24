from collections import Iterator

import scrapy
from betamax import Betamax
from betamax.fixtures.unittest import BetamaxTestCase
from model_mommy import mommy

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
        cls.website: Website = mommy.make(Website, name="expert", domain="expert.ie")
        cls.category: Category = mommy.make(Category, name="Washing Machines")
        mommy.make(Url, url="https://www.harveynorman.ie/home-appliances/appliances/washing-machines/", url_type=CATEGORY, website=cls.website, category=cls.category)

    def test_init_spider(self):
        spider: EcommerceSpider = EcommerceSpider(website=self.website.name)
        self.assertEqual(spider.website, self.website)
        self.assertEqual(spider.allowed_domains, [self.website.domain])

    def test_start_requests(self):
        spider: EcommerceSpider = EcommerceSpider(website=self.website)
        requests = spider.start_requests()
        self.assertIsInstance(requests, Iterator)
        request = next(requests)
        self.assertIsInstance(next(requests), scrapy.Request)
        self.assertEqual(request.callback, spider.parse)
        self.assertEqual(request.cb_kwargs, {'category': self.category})
