from django.db import transaction
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from cms.models import Website
from scraper.spiders.ecommerce import EcommerceSpider


def run_spider(website):
    process = CrawlerProcess(get_project_settings())
    process.crawl(EcommerceSpider, website=website)
    process.start()


@transaction.atomic()
def run():
    for website in Website.objects.filter(publish=True):
        run_spider(website)
