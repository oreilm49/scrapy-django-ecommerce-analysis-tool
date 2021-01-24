from typing import Dict, Union

import scrapy

from cms.constants import CATEGORY, PAGINATION, LINK, TEXT, FLOAT, TABLE, IMAGE, TABLE_VALUE_COLUMN, TABLE_LABEL_COLUMN
from cms.models import Website, Url, Category, Selector, PageDataItem

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
        page_item = ProductPageItem()
        page_item['attributes'] = []
        page_item['category'] = category
        attribute: Dict[str, Union[PageDataItem, str]] = {}
        for data_item in self.website.page_data_items.all():
            data_item: PageDataItem
            selector: Selector = data_item.selector
            if selector.selector_type == TABLE:
                for table_row in response.css(selector.css_selector):
                    attribute.copy()
                    attribute['data_type'] = data_item
                    attribute['value'] = table_row.css(selector.sub_selectors.get(selector_type=TABLE_VALUE_COLUMN).css_selector).extract_first().strip()
                    attribute['label'] = table_row.css(selector.sub_selectors.get(selector_type=TABLE_LABEL_COLUMN).css_selector).extract_first().strip()
                    page_item['attributes'].append(attribute)
            elif selector.selector_type in [TEXT, LINK, IMAGE]:
                attribute.copy()
                attribute['data_type'] = data_item
                attribute['value'] = response.css(selector.css_selector).extract_first().strip()
                page_item['attributes'].append(attribute)
        yield page_item
