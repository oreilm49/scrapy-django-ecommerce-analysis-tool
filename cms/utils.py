import datetime
import re
import requests
from typing import List, Union, Optional, TYPE_CHECKING, Tuple

from django.db.models import QuerySet

if TYPE_CHECKING:
    from cms.models import Category, Product, AttributeType, EprelCategory


def extract_grouper(value: Union[str, float, int], grouper_values: List[Union[str, int]]) -> Optional[Union[str, int, float]]:
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


def products_grouper(product: 'Product', attribute: Optional['AttributeType'], attribute_values: Optional[List[Union[str, int]]]) -> Optional[Union[str, int, float]]:
    """
    Extracts a grouper key for product by comparing attribute value against list of attribute_values.
    :param product: Product object.
    :param attribute: AttributeType object. Has a relation to ProductAttribute or WebsiteProductAttribute.
    :param attribute_values: List of possible grouper values.
    :return: single grouper value from list of attribute_values
    """
    if not attribute:
        return None
    if attribute.name == 'price':
        return extract_grouper(product.current_average_price_int, attribute_values)
    if attribute.name == 'brand':
        return extract_grouper(product.brand.name, attribute_values) if product.brand else None
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


def camel_case_to_sentence(string: str) -> str:
    return re.sub('([a-z]+)([A-Z])', r'\1 \2', string).lower()


def filename_from_path(path: str) -> str:
    return path.split("/")[-1]


def get_eprel_api_url_and_category(eprel_code: str, category: 'Category') -> Optional[Tuple['EprelCategory', str]]:
    from cms.constants import EPREL_API_ROOT_URL
    for eprel_category in category.eprel_names.all():
        url = f"{EPREL_API_ROOT_URL}{eprel_category.name}/{eprel_code}"
        response = requests.get(url)
        if response.status_code == 200:
            return eprel_category, url
