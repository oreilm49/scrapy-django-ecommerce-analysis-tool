from typing import Optional, Union

from django import template
from django.utils.html import format_html

from cms.dashboard.constants import COMPETITIVE_SCORE_GOOD, COMPETITIVE_SCORE_ATTENTION, COMPETITIVE_SCORE_BAD, \
    CategoryTableProduct, CategoryTableEmpty
from cms.models import Product, ProductAttribute

register = template.Library()


@register.simple_tag(takes_context=True)
def product_specs(context: dict, product: Product):
    specs_limit: int = 5
    html = ""
    for index, product_attribute in enumerate(product.top_attributes):
        product_attribute: ProductAttribute
        if index > specs_limit:
            break
        html += f"<div style='display: block'>{product_attribute.display if product_attribute else '-'}</div>"
    return format_html(html)


@register.simple_tag(takes_context=True)
def product_attribute(context: dict, product_attribute: ProductAttribute):
    if product_attribute.attribute_type.unit:
        if product_attribute.attribute_type.unit.is_bool:
            html = '<i class="fa fa-check-circle text-success" aria-hidden="true"></i>'
        else:
            html = f'{product_attribute.data["value"]} {product_attribute.attribute_type.unit}'
    else:
        html = f'{product_attribute.data["value"]}'
    return format_html(html)


@register.filter
def cluster_score_icon(score: str) -> Optional[str]:
    if score is COMPETITIVE_SCORE_GOOD:
        return 'fa fa-check'
    elif score is COMPETITIVE_SCORE_ATTENTION:
        return 'fa fa-exclamation'
    elif score is COMPETITIVE_SCORE_BAD:
        return 'fa fa-times'


@register.filter
def cluster_score_class(score: str) -> Optional[str]:
    if score is COMPETITIVE_SCORE_GOOD:
        return 'success'
    elif score is COMPETITIVE_SCORE_ATTENTION:
        return 'warning'
    elif score is COMPETITIVE_SCORE_BAD:
        return 'danger'


@register.filter
def is_empty_cell(product: Union[CategoryTableProduct, CategoryTableEmpty]) -> bool:
    return isinstance(product, CategoryTableEmpty)
