from typing import Union

from django.db.models import Q

from cms.data_processing.constants import UnitValue, Value, RangeUnitValue
from cms.data_processing.units import UnitManager
from cms.models import AttributeType, ProductAttribute


def create_product_attribute(product, attribute_label: str, attribute_value: Union[str, int, float]) -> None:
    attribute_type: AttributeType = AttributeType.objects.custom_get_or_create(attribute_label)
    product_attribute_exists: bool = ProductAttribute.objects.filter(attribute_type=attribute_type, product=product).exists()
    if product_attribute_exists:
        return

    processed_unit: Union[UnitValue, Value, RangeUnitValue] = UnitManager().get_processed_unit_and_value(attribute_value, unit=attribute_type.unit)
    if not attribute_type.unit and isinstance(processed_unit, (UnitValue, RangeUnitValue)):
        attribute_type.unit = processed_unit.unit
        attribute_type.save()
    if isinstance(processed_unit, RangeUnitValue):
        name_low: str = f"{attribute_type.name} - low"
        name_high: str = f"{attribute_type.name} - high"
        if ProductAttribute.objects.filter(Q(attribute_type__name=name_low) | Q(attribute_type__name=name_high), product=product).exists():
            return

        attribute_type_low: AttributeType = AttributeType.objects.custom_get_or_create(f"{attribute_label} - low", unit=processed_unit.unit)
        attribute_type_high: AttributeType = AttributeType.objects.custom_get_or_create(f"{attribute_label} - high", unit=processed_unit.unit)
        ProductAttribute.objects.custom_get_or_create(product=product, attribute_type=attribute_type_low, value=processed_unit.value_low)
        ProductAttribute.objects.custom_get_or_create(product=product, attribute_type=attribute_type_high, value=processed_unit.value_high)
    else:
        ProductAttribute.objects.custom_get_or_create(product=product, attribute_type=attribute_type, value=processed_unit.value)
