from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.ecommerce import EcommerceSpider


def run_spider(website):
    process = CrawlerProcess(get_project_settings())
    process.crawl(EcommerceSpider, website=website)
    process.start()
