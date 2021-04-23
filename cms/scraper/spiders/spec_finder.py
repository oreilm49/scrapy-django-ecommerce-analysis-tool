import re
from difflib import SequenceMatcher
from typing import List, Optional

import scrapy

from cms.models import Category
from cms.scraper.items import EnergyLabelItem
from cms.scraper.spiders.ecommerce import EcommerceSpider


class SpecFinderSpider(EcommerceSpider):
    name = 'spec_finder'

    def __init__(self, *args, category: Category, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [self.allowed_domains]
        self.category = category

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_category_link, cb_kwargs={'category': self.category})

    def parse_category_link(self, response, category: Category = None, **kwargs) -> scrapy.Request:
        for name in category.searchable_names:
            href: Optional[str] = response.xpath(f"//nav//a[contains(text(), '{name}')]/@href").get()
            if href:
                yield response.follow(response.urljoin(href), self.parse_product_list, cb_kwargs={'category': category})

    def parse_product_list(self, response, category: Category = None, **kwargs):
        """
        Extracts a list of similar hrefs from the main content area of the page.
        Hopefully, they are links to product pages.
        """
        hrefs: List[str] = response.xpath("//a//@href[not(ancestor::header)][not(ancestor::nav)][not(ancestor::aside)][not(ancestor::*[@id='footer'])][not(ancestor::*[@id='pagination'])][not(ancestor::*[@class='pagination'])]").getall()
        grouped_hrefs: List[List[str]] = []
        for href in hrefs:
            if not len(grouped_hrefs):
                grouped_hrefs.append([href])
            else:
                for i in range(0, len(grouped_hrefs)):
                    score = SequenceMatcher(None, href, grouped_hrefs[i][0]).ratio()
                    if score < 0.5:
                        if i == len(grouped_hrefs) - 1:
                            grouped_hrefs.append([href])
                    else:
                        if score != 1:
                            grouped_hrefs[i].append(href)
        # we only want the list with the most number of hrefs, as this
        # is most likely to be the list of product links.
        longest_list = max(grouped_hrefs, key=lambda group: len(group))
        for href in longest_list:
            yield response.follow(response.urljoin(href), self.parse_product, cb_kwargs={'category': category, 'href': href})

    def parse_product_energy_label(self, response, category: Category = None, href: str = None, **kwargs):
        pdf_urls: List[str] = response.xpath('//a[contains(@href, ".pdf")]/@href').getall()
        for pdf in pdf_urls:
            if re.search(r"energy.*label", pdf):
                item = EnergyLabelItem()
                item['energy_label_urls'] = [pdf]
                item['category'] = category
                item['website'] = self.website
                item['product_link'] = href
                yield item
                break
