import scrapy

from cms.constants import CATEGORY
from cms.models import Website
from scraper.scraper.exceptions import WebsiteNotProvidedInArguments


class EcommerceSpider(scrapy.Spider):
    name = 'ecommerce'
    allowed_domains = []
    start_urls = []

    def __init__(self, website: Website = None, **kwargs):
        super().__init__(**kwargs)
        if not website:
            raise WebsiteNotProvidedInArguments
        self.website = website
        self.allowed_domains = [website.domain]
        self.start_urls = [website.urls.filter(url_type=CATEGORY).values_list("url")]

    def parse(self, response, **kwargs):
        pass
