from django.db.models import Q

from cms.constants import ONCE
from cms.models import Product, ProductAttribute
from scraper.items import ProductPageItem


class ScraperPipeline:

    def process_item(self, item, spider):
        if isinstance(item, ProductPageItem):
            product_check = Product.objects.filter(category=item['category'])\
                .filter(Q(model=item['model']) | Q(alternate_models__contains=[item['model']]))
            if not product_check.exists():
                product: Product = Product.objects.create(model=item['model'], category=item['category'])
                product.save()
            else:
                product: Product = product_check.first()

            for attribute in item['attributes']:
                unrepeatable_check: bool = ProductAttribute.objects.filter(
                    product=product,
                    data_type__id=attribute['data_type'].pk,
                    data_type__repeat=ONCE
                ).exists()
                if not unrepeatable_check:
                    product_attribute: ProductAttribute = ProductAttribute.objects.create(
                        product=product,
                        data_type=attribute['data_type'],
                        value=attribute['value']
                    )
                    product_attribute.save()
