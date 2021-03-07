import scrapy


class ProductPageItem(scrapy.Item):
    model = scrapy.Field()
    product = scrapy.Field()
    category = scrapy.Field()
    website = scrapy.Field()
    attributes = scrapy.Field()
    website_attributes = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
