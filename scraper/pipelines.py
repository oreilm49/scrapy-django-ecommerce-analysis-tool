from typing import Union, Dict, Optional

from django.db.models import Q
from pint import UnitRegistry, Quantity

from cms.constants import PRICE, IMAGE
from cms.data_processing.constants import UnitValue
from cms.models import Product, ProductAttribute, Unit, WebsiteProductAttribute, Selector, AttributeType
from scraper.items import ProductPageItem


class ScraperPipeline:

    def __init__(self) -> None:
        super().__init__()
        self.ureg = UnitRegistry()
        self.ureg.define('decibels = 1 * decibel = db')

    def process_item(self, item, spider):
        if isinstance(item, ProductPageItem):
            product: Product = self.get_product(item)
            for attribute in item['attributes']:
                attribute: Dict
                processed_unit: Optional[UnitValue] = self.get_processed_unit_and_value(attribute['value'])
                attribute_type: AttributeType = self.get_attribute_type(attribute['label'], unit=processed_unit.unit if processed_unit else None)
                product_attribute_exists: bool = ProductAttribute.objects.filter(attribute_type=attribute_type, product=product).exists()
                if product_attribute_exists:
                    continue

                value = processed_unit.value if processed_unit else attribute['value']
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
                    price_attribute_type, _ = AttributeType.objects.get_or_create(name="price", unit=item['website'].currency)
                    price_attribute: WebsiteProductAttribute = WebsiteProductAttribute.objects.create(
                        website=selector.website,
                        product=product,
                        attribute_type=price_attribute_type,
                        value=website_attribute['value']
                    )
                    price_attribute.save()

    def get_product(self, item: ProductPageItem) -> Product:
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
        return product

    def get_processed_unit_and_value(self, value: str) -> Optional[UnitValue]:
        try:
            quantity: Quantity = self.ureg(value).to_root_units()
            name: str = str(quantity.units)
            value: Union[str, int, float] = quantity.magnitude
            unit, _ = Unit.objects.get_or_create(name=name, data_type=type(value).__qualname__)
            return UnitValue(unit=unit, value=value)
        except Exception as e:
            return None

    def get_attribute_type(self, label: str) -> AttributeType:
        attribute_type_check = AttributeType.objects.filter(Q(name=label) | Q(alternate_names__contains=[label]))
        if not attribute_type_check.exists():
            attribute_type, _ = AttributeType.objects.get_or_create(name=label)
            attribute_type.save()
        else:
            attribute_type: AttributeType = attribute_type_check.first()
        return attribute_type
