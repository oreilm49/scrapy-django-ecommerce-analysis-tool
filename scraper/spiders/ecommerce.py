from typing import Iterator, Optional

import scrapy

from cms.constants import CATEGORY, PAGINATION, LINK, TABLE, TABLE_VALUE_COLUMN, TABLE_LABEL_COLUMN, MODEL, PRICE, IMAGE
from cms.models import Website, Url, Category, Selector

from scraper.exceptions import WebsiteNotProvidedInArguments
from scraper.items import ProductPageItem


class EcommerceSpider(scrapy.Spider):
    name = 'ecommerce'
    allowed_domains = []
    start_urls = []

    def __init__(self, website: str = None, **kwargs):
        super().__init__(**kwargs)
        if not website:
            raise WebsiteNotProvidedInArguments
        self.website: Website = Website.objects.get(name=website)
        self.allowed_domains = [self.website.domain]

    def start_requests(self):
        for url in self.website.urls.filter(url_type=CATEGORY):
            url: Url
            yield scrapy.Request(url.url, callback=self.parse, cb_kwargs={'category': url.category})

    def parse(self, response, category: Category = None, **kwargs) -> Iterator[scrapy.Request]:
        element: scrapy.selector.unified.Selector
        for element in response.css(self.website.selectors.filter(selector_type=PAGINATION).first().css_selector):
            href: Optional[str] = element.attrib.get('href')
            if href:
                yield response.follow(href, self.parse, cb_kwargs={'category': category})

        for element in response.css(self.website.selectors.filter(selector_type=LINK).first().css_selector):
            href: Optional[str] = element.attrib.get('href')
            if href:
                yield response.follow(href, self.parse_product, cb_kwargs={'category': category})

    def parse_product(self, response, category: Category = None, **kwargs) -> Iterator[ProductPageItem]:
        for model_selector in self.website.selectors.filter(selector_type=MODEL):
            model_selector: Selector
            model: Optional[str] = response.css(model_selector.css_selector).get()
            if model:
                page_item = ProductPageItem()
                page_item['model'] = model
                page_item['website'] = self.website
                page_item['attributes'] = []
                page_item['website_attributes'] = []
                page_item['category'] = category
                for selector in self.website.selectors.exclude(selector_type=MODEL).all():
                    selector: Selector
                    if selector.selector_type == TABLE:
                        for table_row in response.css(selector.css_selector):
                            table_row: scrapy.selector.unified.Selector
                            value: Optional[str] = table_row.css(selector.sub_selectors.get(selector_type=TABLE_VALUE_COLUMN).css_selector).get()
                            label: Optional[str] = table_row.css(selector.sub_selectors.get(selector_type=TABLE_LABEL_COLUMN).css_selector).get()
                            if value and label:
                                page_item['attributes'].append({'value': value.strip().lower(), 'label': label.strip().lower()})
                    elif selector.selector_type in [PRICE, LINK, IMAGE]:
                        value: Optional[str] = response.css(selector.css_selector).get()
                        if value:
                            page_item['website_attributes'].append({'value': value.strip().lower(), 'selector': selector})
                yield page_item
                break
