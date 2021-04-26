from typing import Dict
import scrapy

from cms.models import Website, Category, SpiderResult
from cms.scraper.exceptions import WebsiteNotProvidedInArguments


class BaseSpiderMixin:
    name = 'base'
    allowed_domains = []
    start_urls = []
    results: Dict[Category, int] = {}

    def __init__(self, website: str = None, **kwargs):
        super().__init__(**kwargs)
        if not website:
            raise WebsiteNotProvidedInArguments
        self.website: Website = Website.objects.get(name=website)
        self.allowed_domains = [self.website.domain.split("/")[0]]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpiderMixin, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.handle_spider_closed, scrapy.spiders.signals.spider_closed)
        return spider

    def handle_spider_closed(self, reason):
        for category, items_scraped in self.results.items():
            SpiderResult.objects.create(
                spider_name=self.name,
                website=self.website,
                category=category,
                items_scraped=items_scraped
            )
