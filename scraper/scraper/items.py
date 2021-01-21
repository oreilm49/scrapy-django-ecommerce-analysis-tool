import scrapy
from scrapy_djangoitem import DjangoItem

from cms.models import Product, ProductAttribute


class ProductItem(DjangoItem):
    django_model = Product


class ProductAttributeItem(DjangoItem):
    django_model = ProductAttribute
