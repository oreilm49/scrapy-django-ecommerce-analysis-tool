from celery import shared_task
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from cms.models import Website
from cms.scraper.spiders.ecommerce import EcommerceSpider


def crawl_website(website: Website):
    process = CrawlerProcess(get_project_settings())
    process.crawl(EcommerceSpider, website=website)
    process.start()


@shared_task
def crawl_websites():
    for website in Website.objects.filter(publish=True):
        p = Process(target=crawl_website, args=(website, ))
        p.start()
        p.join()
