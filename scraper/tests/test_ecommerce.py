from collections import Iterator
from django.test import TestCase

from cms.constants import CATEGORY
from cms.models import Website, Url, Category
from cms.scripts.load_cms import set_up_websites

from scraper.spiders.ecommerce import EcommerceSpider


class TestEcommerce(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        set_up_websites()
        cls.website: Website = Website.objects.first()
        cls.category: Category = Category.objects.first()
        cls.url: Url = Url.objects.get(url_type=CATEGORY)
        cls.product_url: str = cls.url.url + "whirlpool-8kg-freestanding-washing-machine-ffb8448wvuk.html"

    def test_init_spider(self):
        spider: EcommerceSpider = EcommerceSpider(website=self.website.name)
        self.assertEqual(spider.website, self.website)
        self.assertEqual(spider.allowed_domains, [self.website.domain])

    def test_start_requests(self):
        spider: EcommerceSpider = EcommerceSpider(website=self.website.name)
        requests = spider.start_requests()
        self.assertIsInstance(requests, Iterator)
