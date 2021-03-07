from typing import List, Optional

from cms.models import ProductAttribute


def get_brands() -> List[Optional[str]]:
    return ProductAttribute.objects.filter(attribute_type__name="brand").values_list('data__value', flat=True).distinct()
