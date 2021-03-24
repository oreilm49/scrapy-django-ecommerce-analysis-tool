from celery import shared_task, group
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from cms.models import Website
from cms.scraper.spiders.ecommerce import EcommerceSpider


@shared_task
def crawl_websites():
    process = CrawlerProcess(get_project_settings())
    for website in Website.objects.filter(publish=True):
        process.crawl(EcommerceSpider, website=website)
    process.start()
