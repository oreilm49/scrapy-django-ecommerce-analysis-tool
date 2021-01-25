import scrapy


class ProductPageItem(scrapy.Item):
    model = scrapy.Field()
    price = scrapy.Field()
    category = scrapy.Field()
    attributes = scrapy.Field()
