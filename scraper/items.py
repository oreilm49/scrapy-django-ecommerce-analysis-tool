import scrapy


class ProductPageItem(scrapy.Item):
    model = scrapy.Field()
    category = scrapy.Field()
    attributes = scrapy.Field()
    website_attributes = scrapy.Field()
