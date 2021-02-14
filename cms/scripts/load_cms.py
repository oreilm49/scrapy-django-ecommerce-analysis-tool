from django.db import transaction

from cms.constants import CATEGORY, TABLE_LABEL_COLUMN, TABLE_VALUE_COLUMN, TABLE, LINK, PAGINATION, PRICE, MODEL, \
    HOURLY, IMAGE
from cms.form_widgets import FloatInput
from cms.models import Website, Category, Url, Selector, Unit
from cms.utils import get_dotted_path


def set_up_websites():
    currency, _ = Unit.objects.get_or_create(name="€", alternate_names=["euro"], widget=get_dotted_path(FloatInput), repeat=HOURLY)
    harvey_norman, _ = Website.objects.get_or_create(name="harvey_norman", domain="harveynorman.ie", currency=currency)
    laundry, _ = Category.objects.get_or_create(name="laundry")
    washing_machines, _ = Category.objects.get_or_create(name="washing machines", parent=laundry, alternate_names=["washers", "front loaders"])
    Url.objects.get_or_create(url="https://www.harveynorman.ie/home-appliances/appliances/washing-machines/", url_type=CATEGORY, website=harvey_norman, category=washing_machines)

    table_selector, _ = Selector.objects.get_or_create(selector_type=TABLE, css_selector="#content_features table.table-product-features tr", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=TABLE_LABEL_COLUMN, css_selector="th strong::text", website=harvey_norman, parent=table_selector)
    Selector.objects.get_or_create(selector_type=TABLE_VALUE_COLUMN, css_selector="td::text", website=harvey_norman, parent=table_selector)
    Selector.objects.get_or_create(selector_type=PRICE, css_selector=".price-num:nth-child(2)::text", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=MODEL, css_selector=".product-id.meta::text", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=LINK, css_selector=".product-info a", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=PAGINATION, css_selector="li a.next", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=IMAGE, css_selector='.cm-image-previewer.image-magnifier-image::attr(href)', website=harvey_norman)


@transaction.atomic()
def run():
    set_up_websites()
