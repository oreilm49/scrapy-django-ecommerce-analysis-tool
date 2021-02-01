from typing import Union, Dict

from django.db import transaction
from django.db.models import Q

from cms.constants import PRICE, IMAGE
from cms.data_processing.constants import UnitValue, Value, RangeUnitValue
from cms.data_processing.units import UnitManager
from cms.models import Product, ProductAttribute, Selector, AttributeType
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

                processed_unit: Union[UnitValue, Value, RangeUnitValue] = UnitManager().get_processed_unit_and_value(attribute['value'], unit=attribute_type.unit)
                if not attribute_type.unit and isinstance(processed_unit, (UnitValue, RangeUnitValue)):
                    attribute_type.unit = processed_unit.unit
                    attribute_type.save()
                if isinstance(processed_unit, RangeUnitValue):
                    name_low: str = f"{attribute_type.name} - low"
                    name_high: str = f"{attribute_type.name} - high"
                    if ProductAttribute.objects.filter(Q(attribute_type__name=name_low) | Q(attribute_type__name=name_high), product=product).exists():
                        continue

                    attribute_type_low: AttributeType = AttributeType.objects.get_or_create_by_name(f"{attribute['label']} - low")
                    attribute_type_high: AttributeType = AttributeType.objects.get_or_create_by_name(f"{attribute['label']} - high")
                    ProductAttribute.objects.create(product=product, attribute_type=attribute_type_low, value=processed_unit.value_low)
                    ProductAttribute.objects.create(product=product, attribute_type=attribute_type_high, value=processed_unit.value_high)
                else:
                    ProductAttribute.objects.create(product=product, attribute_type=attribute_type, value=processed_unit.value)

            for website_attribute in item['website_attributes']:
                selector: Selector = website_attribute['selector']
                if selector.selector_type == IMAGE:
                    pass
                elif selector.selector_type == PRICE:
                    price_attribute_type, _ = AttributeType.objects.get_or_create(name="price", unit=item['website'].currency)
                    selector.website.create_product_attribute(product=product, attribute_type=price_attribute_type, value=website_attribute['value'])
