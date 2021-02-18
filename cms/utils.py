import datetime
from typing import List, Union, Optional

from django.db.models import QuerySet


def extract_grouper(value: Union[str, float, int], grouper_values: List[Union[str, int]]) -> Optional[Union[str]]:
    """
    Extracts a grouper value given a value and a list of possible grouper values.
    For number values, a value is matched with the first grouper_value it's less than or equal to.
    :param value:
    :param grouper_values:
    :return:
    """
    groupers_are_nums: bool = type(grouper_values[0]) in [int, float]
    for grouper_value in grouper_values:
        if groupers_are_nums:
            if value <= grouper_value:
                return grouper_value
        elif value == grouper_value:
            return grouper_value


def products_grouper(product: 'Product', attribute: 'AttributeType', attribute_values: List[Union[str, int]]) -> Optional[Union[str]]:
    """
    Extracts a grouper key for product by comparing attribute value against list of attribute_values.
    :param product: Product object.
    :param attribute: AttributeType object. Has a relation to ProductAttribute or WebsiteProductAttribute.
    :param attribute_values: List of possible grouper values.
    :return: single grouper value from list of attribute_values
    """
    product_attribute: QuerySet = attribute.productattributes.filter(product=product)
    if product_attribute.exists():
        return extract_grouper(product_attribute.first().data['value'], attribute_values)
    web_product_attribute: QuerySet = attribute.websiteproductattributes.filter(product=product)
    if web_product_attribute.exists():
        return extract_grouper(web_product_attribute.first().data['value'], attribute_values)


def get_dotted_path(cls: type) -> str:
    """Returns python dotted path for class"""
    return u'{}.{}'.format(cls.__module__, cls.__name__)


def serialized_values_for_attribute_type(values: List[Union[str, int, float, datetime.datetime]], attribute_type: 'AttributeType') -> List[Union[str, int, float, datetime.datetime]]:
    if attribute_type.unit:
        return [attribute_type.unit.serializer.serializer(value) for value in values]
    return values


def is_value_numeric(value: Union[int, str, float]):
    if isinstance(value, datetime.datetime):
        return False
    return type(value) in [float, int] or value.replace('.', '', 1).isdigit()
