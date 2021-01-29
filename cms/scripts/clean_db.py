import os

from django.db import transaction

from cms.models import Product, ProductAttribute, WebsiteProductAttribute, Unit


def clean_db():
    Unit.objects.exclude(name="€").all().delete()
    ProductAttribute.objects.all().delete()
    WebsiteProductAttribute.objects.all().delete()
    Product.objects.all().delete()


@transaction.atomic()
def run():
    if os.environ.get('DEBUG'):
        clean_db()
