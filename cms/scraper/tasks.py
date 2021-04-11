from typing import Optional

import requests
from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from cms.data_processing.utils import create_product_attribute
from cms.models import Website, Product
from cms.scraper.spiders.ecommerce import EcommerceSpider
from cms.utils import camel_case_to_sentence


@shared_task
def crawl_websites():
    process = CrawlerProcess(get_project_settings())
    for website in Website.objects.filter(publish=True):
        process.crawl(EcommerceSpider, website=website)
    process.start()


@shared_task
def crawl_eprel_data():
    for product in Product.objects.published().filter(eprel_scraped=False, eprel_code__isnull=False, eprel_category__isnull=False):
        url: Optional[str] = product.get_eprel_api_url()
        response = requests.get(url)
        for attribute_label, attribute_value in response.json().items():
            attribute_label: str = camel_case_to_sentence(attribute_label)
            if isinstance(attribute_value, (int, float, str)):
                create_product_attribute(product, attribute_label, attribute_value)
        product.eprel_scraped = True
        product.save()
