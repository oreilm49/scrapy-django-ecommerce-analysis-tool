from django.db.models import Q
from cms.models import Product, ProductAttribute
from scraper.scraper.items import ProductItem, ProductAttributeItem


class ScraperPipeline:
    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            if not Product.objects.filter(Q(model=item['model']) | Q(alternate_models=item['model'])).exists():
                item.save()
                return item
        if isinstance(item, ProductAttributeItem):
            pass
        return item
