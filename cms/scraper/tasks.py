from celery import shared_task, group
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from cms.models import Website
from cms.scraper.spiders.ecommerce import EcommerceSpider


@shared_task
def crawl_website(pk: int):
    process = CrawlerProcess(get_project_settings())
    process.crawl(EcommerceSpider, website=Website.objects.get(pk=pk))
    process.start()


@shared_task
def crawl_websites():
    group(crawl_website.s(website.pk) for website in Website.objects.filter(publish=True))()
