import re
from typing import List

from cms.models import Category
from cms.scraper.items import EnergyLabelItem
from cms.scraper.spiders.base import BaseSpiderMixin


from scrapy.spiders import SitemapSpider


class SpecFinderSpider(BaseSpiderMixin, SitemapSpider):
    name = 'spec_finder'
    sitemap_rules = [('a^', 'parse')]

    def __init__(self, *args, category_name: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.category: Category = Category.objects.get(name=category_name)
        self.results[self.category] = 0
        self.sitemap_urls = [f"http://{self.website.domain}/sitemap.xml"]
        self.sitemap_rules = [("".join(rf'(.*?){name_slice}(.*?)' for name_slice in name.split(" ")), 'parse')
                              for name in self.category.searchable_names]

    def parse(self, response, **kwargs):
        pdf_urls: List[str] = response.xpath('//a[contains(@href, ".pdf")]/@href').getall()
        for pdf in pdf_urls:
            if re.search(r"energy.*label", pdf):
                item = EnergyLabelItem()
                item['energy_label_urls'] = [pdf]
                item['category'] = self.category
                item['brand'] = self.website.brands.first()
                self.results[self.category] += 1
                yield item
                break
