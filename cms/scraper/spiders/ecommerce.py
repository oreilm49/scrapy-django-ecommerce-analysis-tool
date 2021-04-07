import re
from typing import Iterator, Optional, Dict

import scrapy

from cms.constants import CATEGORY, PAGINATION, LINK, TABLE, TABLE_VALUE_COLUMN, TABLE_LABEL_COLUMN, MODEL, PRICE, \
    IMAGE, TABLE_VALUE_COLUMN_BOOL, ENERGY_lABEL_PDF
from cms.models import Website, Url, Category, Selector, SpiderResult

from cms.scraper.exceptions import WebsiteNotProvidedInArguments
from cms.scraper.items import ProductPageItem


class EcommerceSpider(scrapy.Spider):
    name = 'ecommerce'
    allowed_domains = []
    start_urls = []
    results: Dict[Category, int] = {}

    def __init__(self, website: str = None, **kwargs):
        super().__init__(**kwargs)
        if not website:
            raise WebsiteNotProvidedInArguments
        self.website: Website = Website.objects.get(name=website)
        self.allowed_domains = [self.website.domain]

    def start_requests(self):
        for url in self.website.urls.filter(url_type=CATEGORY):
            url: Url
            self.results[url.category] = 0
            yield scrapy.Request(url.url, callback=self.parse, cb_kwargs={'category': url.category})

    def parse(self, response, category: Category = None, **kwargs) -> Iterator[scrapy.Request]:
        element: scrapy.selector.unified.Selector
        pagination_selectors = self.website.selectors.filter(selector_type=PAGINATION)
        if pagination_selectors.exists():
            for element in response.css(pagination_selectors.first().css_selector):
                href: Optional[str] = element.attrib.get('href')
                if href:
                    yield response.follow(response.urljoin(href), self.parse, cb_kwargs={'category': category})

        for element in response.css(self.website.selectors.filter(selector_type=LINK).first().css_selector):
            href: Optional[str] = element.attrib.get('href')
            if href:
                yield response.follow(response.urljoin(href), self.parse_product, cb_kwargs={'category': category})

    def parse_product(self, response, category: Category = None, **kwargs) -> Iterator[ProductPageItem]:
        for model_selector in self.website.selectors.filter(selector_type=MODEL):
            model_selector: Selector
            model: Optional[str] = response.css(model_selector.css_selector).get()
            if model:
                page_item = ProductPageItem()
                page_item['model'] = model.strip().lower()
                page_item['website'] = self.website
                page_item['attributes'] = []
                page_item['website_attributes'] = []
                page_item['image_urls'] = []
                page_item['category'] = category
                page_item['file_urls'] = []
                for selector in self.website.selectors.exclude(selector_type=MODEL).all():
                    selector: Selector
                    if selector.selector_type == TABLE:
                        for table_row in response.css(selector.css_selector):
                            table_row: scrapy.selector.unified.Selector
                            value: Optional[str] = table_row.css(selector.sub_selectors.get(selector_type=TABLE_VALUE_COLUMN).css_selector).get()
                            label: Optional[str] = table_row.css(selector.sub_selectors.get(selector_type=TABLE_LABEL_COLUMN).css_selector).get()
                            # strip whitespace so empty strings with only spacing aren't processed further.
                            value = value.strip().lower() if value else None
                            label = label.strip().lower() if label else None
                            if not value and selector.sub_selectors.filter(selector_type=TABLE_VALUE_COLUMN_BOOL).exists():
                                bool_selector: Selector = selector.sub_selectors.get(selector_type=TABLE_VALUE_COLUMN_BOOL)
                                value = table_row.css(bool_selector.css_selector).get().strip().lower()
                                value = "true" if re.search(bool_selector.regex, value) else None
                            if value and label:
                                page_item['attributes'].append({'value': value, 'label': label})
                    elif selector.selector_type in [PRICE, LINK, IMAGE, ENERGY_lABEL_PDF]:
                        value: Optional[str] = response.css(selector.css_selector).get()
                        if value and selector.selector_type == IMAGE:
                            # don't .lower() image urls, filename urls are case sensitive
                            page_item['image_urls'].append(response.urljoin(value.strip()))
                        elif value and selector.selector_type == ENERGY_lABEL_PDF:
                            page_item['file_urls'].append(response.urljoin(value.strip()))
                        elif value:
                            page_item['website_attributes'].append({'value': value.strip().lower(), 'selector': selector})
                self.results[category] += 1
                yield page_item
                break

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(EcommerceSpider, cls).from_crawler(crawler, *args, **kwargs)
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
