from typing import Optional

import requests
from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from cms.constants import WEBSITE_TYPE_RETAILER, WEBSITE_TYPE_SUPPLIER
from cms.data_processing.utils import create_product_attribute
from cms.models import Website, Product, Brand, Category
from cms.scraper.spiders.ecommerce import EcommerceSpider
from cms.scraper.spiders.spec_finder import SpecFinderSpider
from cms.utils import camel_case_to_sentence


@shared_task
def crawl_websites():
    process = CrawlerProcess(get_project_settings())
    for website in Website.objects.published().filter(website_type=WEBSITE_TYPE_RETAILER):
        process.crawl(EcommerceSpider, website=website)
    process.start()


def create_product_attributes(product: Product, data: dict) -> None:
    for attribute_label, attribute_value in data.items():
        attribute_label: str = camel_case_to_sentence(attribute_label)
        if isinstance(attribute_value, (int, float, str)):
            create_product_attribute(product, attribute_label, attribute_value)


@shared_task
def crawl_eprel_data():
    for product in Product.objects.published().filter(eprel_scraped=False, eprel_code__isnull=False):
        url: Optional[str] = product.get_eprel_api_url()
        response = requests.get(url)
        create_product_attributes(product, response.json())
        product.eprel_scraped = True
        product.save()


@shared_task
def crawl_brand_websites():
    process = CrawlerProcess(get_project_settings())
    for brand in Brand.objects.published().filter(website__website_type=WEBSITE_TYPE_SUPPLIER):
        for category in Category.objects.filter(urls__isnull=False):
            process.crawl(SpecFinderSpider, website=brand.website.name, category_name=category.name)
    process.start()
