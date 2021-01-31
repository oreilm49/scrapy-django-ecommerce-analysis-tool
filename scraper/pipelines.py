from typing import Union, Dict

from django.db import transaction

from cms.constants import PRICE, IMAGE
from cms.data_processing.constants import UnitValue, Value
from cms.data_processing.units import UnitManager
from cms.models import Product, ProductAttribute, WebsiteProductAttribute, Selector, AttributeType
from scraper.items import ProductPageItem


class ScraperPipeline:

    @transaction.atomic
    def process_item(self, item, spider):
        if isinstance(item, ProductPageItem):
            product: Product = Product.objects.get_or_create_for_item(item)
            for attribute in item['attributes']:
                attribute: Dict
                attribute_type: AttributeType = AttributeType.objects.get_or_create_by_name(attribute['label'])
                product_attribute_exists: bool = ProductAttribute.objects.filter(attribute_type=attribute_type, product=product).exists()
                if product_attribute_exists:
                    continue

                processed_unit: Union[UnitValue, Value] = UnitManager().get_processed_unit_and_value(attribute['value'], unit=attribute_type.unit)
                if not attribute_type.unit and isinstance(processed_unit, UnitValue):
                    attribute_type.unit = processed_unit.unit
                    attribute_type.save()
                product_attribute: ProductAttribute = ProductAttribute.objects.create(
                    product=product,
                    attribute_type=attribute_type,
                    value=processed_unit.value,
                )
                product_attribute.save()

            for website_attribute in item['website_attributes']:
                selector: Selector = website_attribute['selector']
                if selector.selector_type == IMAGE:
                    pass
                elif selector.selector_type == PRICE:
                    price_attribute_type, _ = AttributeType.objects.get_or_create(name="price", unit=item['website'].currency)
                    price_attribute: WebsiteProductAttribute = WebsiteProductAttribute.objects.create(
                        website=selector.website,
                        product=product,
                        attribute_type=price_attribute_type,
                        value=website_attribute['value']
                    )
                    price_attribute.save()
