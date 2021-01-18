import scrapy


class EcommerceSpider(scrapy.Spider):
    name = 'ecommerce'
    allowed_domains = ['ecommerce.com']
    start_urls = ['http://ecommerce.com/']

    def parse(self, response):
        pass
