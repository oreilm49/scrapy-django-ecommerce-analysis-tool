from django.db.models import Q

from cms.constants import PRICE, IMAGE
from cms.models import Product, ProductAttribute, Unit, WebsiteProductAttribute, Selector
from scraper.items import ProductPageItem


class ScraperPipeline:

    def process_item(self, item, spider):
        if isinstance(item, ProductPageItem):
            product_check = Product.objects.filter(
                Q(model=item['model']) |
                Q(alternate_models__contains=[item['model']]),
                category=item['category']
            )
            if not product_check.exists():
                product: Product = Product.objects.create(model=item['model'], category=item['category'])
                product.save()
            else:
                product: Product = product_check.first()

            for attribute in item['attributes']:
                attribute_exists: bool = ProductAttribute.objects.filter(
                    Q(unit__name=attribute['label']) |
                    Q(unit__alternate_names__contains=[attribute['label']]),
                    product=product
                ).exists()
                if not attribute_exists:
                    unit, _ = Unit.objects.get_or_create(name=attribute['label'])
                    product_attribute: ProductAttribute = ProductAttribute.objects.create(
                        product=product,
                        unit=unit,
                        value=attribute['value'],
                    )
                    product_attribute.save()

            for website_attribute in item['website_attributes']:
                selector: Selector = website_attribute['selector']
                if selector.selector_type == IMAGE:
                    pass
                elif selector.selector_type == PRICE:
                    price_attribute: WebsiteProductAttribute = WebsiteProductAttribute.objects.create(
                        website=selector.website,
                        product=product,
                        unit=selector.website.currency,
                        value=website_attribute['value']
                    )
                    price_attribute.save()
