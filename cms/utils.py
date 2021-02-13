from typing import List, Union, Optional

from django.db.models import QuerySet

from cms.models import Product, AttributeType, ProductAttribute


def extract_grouper(value: Union[str, float, int], grouper_values: List[Union[str]]) -> Optional[Union[str]]:
    """
    Extracts a grouper value given a value and a list of possible grouper values.
    For number values, a value is matched with the first grouper_value it's less than or equal to.
    :param value:
    :param grouper_values:
    :return:
    """
    groupers_are_nums: bool = grouper_values[0].isdigit()
    for grouper_value in grouper_values:
        if groupers_are_nums:
            if int(value) <= int(grouper_value):
                return grouper_value
        elif value == grouper_value:
            return grouper_value


def products_grouper(product: Product, attribute: AttributeType, attribute_values: List[Union[str]]) -> Optional[Union[str]]:
    """
    Extracts a grouper key for product by comparing attribute value against list of attribute_values.
    :param product: Product object.
    :param attribute: AttributeType object. Has a relation to ProductAttribute or WebsiteProductAttribute.
    :param attribute_values: List of possible grouper values.
    :return: single grouper value from list of attribute_values
    """
    product_attribute: QuerySet = attribute.productattributes.filter(product=product)
    if product_attribute.exists():
        return extract_grouper(product_attribute.first().value, attribute_values)
    web_product_attribute: QuerySet = attribute.websiteproductattributes.filter(product=product)
    if web_product_attribute.exists():
        return extract_grouper(web_product_attribute.first().value, attribute_values)
