import scrapy


class ProductPageItem(scrapy.Item):
    model = scrapy.Field()
    price = scrapy.Field()
    attributes = scrapy.Field()
