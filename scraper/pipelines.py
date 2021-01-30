from django.db.models import Q

from cms.constants import PRICE, IMAGE
from cms.models import Product, ProductAttribute, Unit, WebsiteProductAttribute, Selector, AttributeType
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
                label: str = attribute['label']
                value: str = attribute['value']
                attribute_type_check = AttributeType.objects.filter(
                    Q(name=label) |
                    Q(alternate_names__contains=[label]),
                )
                if not attribute_type_check.exists():
                    attribute_type: AttributeType = AttributeType.objects.create(name=label)
                    attribute_type.save()
                else:
                    attribute_type: AttributeType = attribute_type_check.first()
                    
                attribute_exists: bool = ProductAttribute.objects.filter(attribute_type=attribute_type, product=product).exists()
                if not attribute_exists:
                    attribute_type, _ = Unit.objects.get_or_create(name=label)
                    product_attribute: ProductAttribute = ProductAttribute.objects.create(
                        product=product,
                        attribute_type=attribute_type,
                        value=value,
                    )
                    product_attribute.save()

            for website_attribute in item['website_attributes']:
                selector: Selector = website_attribute['selector']
                if selector.selector_type == IMAGE:
                    pass
                elif selector.selector_type == PRICE:
                    attribute_type: AttributeType = AttributeType.objects.get(name="price", unit=selector.website.currency)
                    price_attribute: WebsiteProductAttribute = WebsiteProductAttribute.objects.create(
                        website=selector.website,
                        product=product,
                        attribute_type=attribute_type,
                        value=website_attribute['value']
                    )
                    price_attribute.save()
