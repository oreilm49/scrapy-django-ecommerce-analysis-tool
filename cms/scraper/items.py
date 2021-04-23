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
    energy_label_urls = scrapy.Field()


class EnergyLabelItem(scrapy.Item):
    website = scrapy.Field()
    category = scrapy.Field()
    energy_label_urls = scrapy.Field()
    product_link = scrapy.Field()
