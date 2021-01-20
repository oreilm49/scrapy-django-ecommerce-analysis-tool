import scrapy

from cms.constants import CATEGORY, PAGINATION, LINK
from cms.models import Website, Url, Category
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

    def start_requests(self):
        for url in self.website.urls.filter(url_type=CATEGORY):
            url: Url
            yield scrapy.Request(url.url, callback=self.parse, cb_kwargs={'category': url.category})

    def parse(self, response, category: Category = None, **kwargs):
        for href in response.css(self.website.selectors.filter(selector_type=PAGINATION).first().css_selector):
            yield response.follow(href, self.parse, cb_kwargs={'category': category})

        for href in response.css(self.website.selectors.filter(selector_type=LINK, name="product").first().css_selector):
            yield response.follow(href, self.parse_product, cb_kwargs={'category': category})

    def parse_product(self, response, category: Category = None, **kwargs):
        pass
