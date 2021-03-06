from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from cms.models import Website
from scraper.spiders.ecommerce import EcommerceSpider


def crawl_website(website: Website):
    process = CrawlerProcess(get_project_settings())
    process.crawl(EcommerceSpider, website=website)
    process.start()


@shared_task
def crawl_websites():
    for website in Website.objects.filter(publish=True):
        crawl_website(website)
