from typing import Optional

from django.db import transaction

from cms.constants import CATEGORY, TABLE_LABEL_COLUMN, TABLE_VALUE_COLUMN, TABLE, LINK, PAGINATION, PRICE, MODEL, \
    HOURLY, IMAGE, SCORING_NUMERICAL_HIGHER, SCORING_NUMERICAL_LOWER
from cms.form_widgets import FloatInput
from cms.models import Website, Category, Url, Selector, Unit, Product, ProductAttribute, AttributeType, \
    WebsiteProductAttribute, CategoryAttributeConfig, EprelCategory
from cms.utils import get_dotted_path


products = [
    ["P35106SKW", 6, 1000, 71, 209.95, "powerpoint"],
    ["WM1003WH", 5, 1000, 75, 209.95, "nordmende"],
    ["WTK62051W", 6, 1200, 75, 219.95, "beko"],
    ["P35127SKW", 7, 1200, 80, 229.99, "powerpoint"],
    ["WTL72051W", 7, 1200, 80, 229.95, "beko"],
    ["WTL82051W", 8, 1200, 80, 229.95, "beko"],
    ["IWC71452WUKN", 7, 1400, 95, 249.99, "indesit"],
    ["WM1477WH", 7, 1400, 95, 279.95, "nordmende"],
    ["CS 148TE-80", 8, 1400, 95, 289.95, "candy"],
    ["WM1277BL", 7, 1200, 85, 289.95, "nordmende"],
    ["H3W 49TE-80", 9, 1400, 100, 299.99, "hoover"],
    ["WEY86052W", 8, 1600, 100, 299.99, "beko"],
    ["WTG941B3W", 9, 1400, 120, 299.99, "beko"],
    ["IWC91482ECO", 9, 1400, 110, 299.99, "indesit"],
    ["MTWC91483WUK", 9, 1400, 109, 299.99, "indesit"],
    ["WTL74051B", 7, 1400, 100, 299.99, "beko"],
    ["WMT1270BL", 7, 1200, 105, 329.99, "beko"],
]


def set_up_attributes():
    load_size_unit, _ = Unit.objects.get_or_create(name="kilogram", widget=get_dotted_path(FloatInput))
    spin_unit, _ = Unit.objects.get_or_create(name="revolutions_per_minute", widget=get_dotted_path(FloatInput))
    energy_unit, _ = Unit.objects.get_or_create(name="kwh", widget=get_dotted_path(FloatInput))
    currency, _ = Unit.objects.get_or_create(name="€", alternate_names=["euro"], widget=get_dotted_path(FloatInput), repeat=HOURLY)
    AttributeType.objects.get_or_create(name="brand")
    load_size, _ = AttributeType.objects.get_or_create(name="load size", unit=load_size_unit)
    spin, _ = AttributeType.objects.get_or_create(name="spin speed", unit=spin_unit)
    energy, _ = AttributeType.objects.get_or_create(name="energy usage", unit=energy_unit)
    AttributeType.objects.get_or_create(name="price", unit=currency)

    washers = Category.objects.get(name="washing machines")
    CategoryAttributeConfig.objects.create(attribute_type=load_size, category=washers, weight=5, order=1, scoring=SCORING_NUMERICAL_HIGHER)
    CategoryAttributeConfig.objects.create(attribute_type=spin, category=washers, weight=4, order=2, scoring=SCORING_NUMERICAL_HIGHER)
    CategoryAttributeConfig.objects.create(attribute_type=energy, category=washers, weight=3, order=3, scoring=SCORING_NUMERICAL_LOWER)


def make_product(model: str, price: float, load_size: int, spin: int, energy: int, category: Category, brand: str) -> Optional[Product]:
    if Product.objects.filter(model=model).exists():
        return
    product = Product.objects.create(model=model, category=category)
    ProductAttribute.objects.create(product=product, attribute_type=AttributeType.objects.get(name="load size"), data={'value': load_size})
    ProductAttribute.objects.create(product=product, attribute_type=AttributeType.objects.get(name="spin speed"), data={'value': spin})
    ProductAttribute.objects.create(product=product, attribute_type=AttributeType.objects.get(name="energy usage"), data={'value': energy})
    ProductAttribute.objects.create(product=product, attribute_type=AttributeType.objects.get(name="brand"), data={'value': brand})
    website = Website.objects.get(name="harvey_norman")
    WebsiteProductAttribute.objects.create(product=product, website=website, attribute_type=AttributeType.objects.get(name="price"), data={'value': price})
    return product


def set_up_websites():
    currency, _ = Unit.objects.get_or_create(name="€", alternate_names=["euro"], widget=get_dotted_path(FloatInput), repeat=HOURLY)
    harvey_norman, _ = Website.objects.get_or_create(name="harvey_norman", domain="harveynorman.ie", currency=currency)
    laundry, _ = Category.objects.get_or_create(name="laundry")
    washing_machines, _ = Category.objects.get_or_create(name="washing machines", parent=laundry, alternate_names=["washers", "front loaders"])
    EprelCategory.objects.get_or_create(category=washing_machines, name="washingmachines2019")
    EprelCategory.objects.get_or_create(category=washing_machines, name="washingmachines")
    Url.objects.get_or_create(url="https://www.harveynorman.ie/home-appliances/appliances/washing-machines/", url_type=CATEGORY, website=harvey_norman, category=washing_machines)

    table_selector, _ = Selector.objects.get_or_create(selector_type=TABLE, css_selector="#content_features table.table-product-features tr", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=TABLE_LABEL_COLUMN, css_selector="th strong::text", website=harvey_norman, parent=table_selector)
    Selector.objects.get_or_create(selector_type=TABLE_VALUE_COLUMN, css_selector="td::text", website=harvey_norman, parent=table_selector)
    Selector.objects.get_or_create(selector_type=PRICE, css_selector=".price-num:nth-child(2)::text", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=MODEL, css_selector=".product-id.meta::text", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=LINK, css_selector=".product-info a", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=PAGINATION, css_selector="li a.next", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=IMAGE, css_selector='.cm-image-previewer.image-magnifier-image::attr(href)', website=harvey_norman)


def set_up_products():
    category = Category.objects.get(name="washing machines")
    for product in products:
        make_product(product[0], product[4], product[1], product[2], product[3], category, product[5])


@transaction.atomic()
def run():
    set_up_websites()
    set_up_attributes()
    set_up_products()
