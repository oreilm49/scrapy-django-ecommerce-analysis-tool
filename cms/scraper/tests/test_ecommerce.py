from collections import Iterator
from django.test import TestCase
from model_mommy import mommy

from cms.constants import CATEGORY
from cms.models import Website, Url, Category, SpiderResult
from cms.scripts.load_cms import set_up_websites

from cms.scraper.spiders.ecommerce import EcommerceSpider


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
        list(requests)
        self.assertEqual(spider.results, {self.url.category: 0})

    def test_handle_spider_closed(self):
        spider: EcommerceSpider = EcommerceSpider(website=self.website.name)
        cat_1: Category = mommy.make(Category, name="cat_1")
        cat_2: Category = mommy.make(Category, name="cat_2")
        self.assertFalse(SpiderResult.objects.exists())
        spider.results[cat_1] = 20
        spider.results[cat_2] = 0
        spider.handle_spider_closed("")
        self.assertTrue(SpiderResult.objects.filter(spider_name='ecommerce', website=self.website, category=cat_1, items_scraped=20).exists())
        self.assertTrue(SpiderResult.objects.filter(spider_name='ecommerce', website=self.website, category=cat_2, items_scraped=0).exists())
