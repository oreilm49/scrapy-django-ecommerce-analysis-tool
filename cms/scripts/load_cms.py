from django.db import transaction
from model_mommy import mommy

from cms.constants import CATEGORY, TABLE_LABEL_COLUMN, TABLE_VALUE_COLUMN, TABLE, STRING, FLOAT, TEXT, LINK, PAGINATION
from cms.models import Website, Category, Url, Selector, PageDataItem


def set_up_websites():
    harvey_norman, _ = Website.objects.get_or_create(name="harvey_norman", domain="harveynorman.ie")
    laundry, _ = Category.objects.get_or_create(name="laundry")
    washing_machines, _ = Category.objects.get_or_create(name="washing machines", parent=laundry, alternate_names=["washers", "front loaders"])
    Url.objects.get_or_create(url="https://www.harveynorman.ie/home-appliances/appliances/washing-machines/", url_type=CATEGORY, website=harvey_norman, category=washing_machines)

    table_selector, _ = Selector.objects.get_or_create(selector_type=TABLE, css_selector="#content_features table.table-product-features tr", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=TABLE_LABEL_COLUMN, css_selector="th strong::text", website=harvey_norman, parent=table_selector)
    Selector.objects.get_or_create(selector_type=TABLE_VALUE_COLUMN, css_selector="td::text", website=harvey_norman, parent=table_selector)
    PageDataItem.objects.get_or_create(name="table", data_type=STRING, website=harvey_norman, selector=table_selector)
    PageDataItem.objects.get_or_create(name="price", data_type=FLOAT, website=harvey_norman, selector=mommy.make(
        Selector, selector_type=TEXT, css_selector=".price-num:nth-child(2)::text", website=harvey_norman
    ))
    PageDataItem.objects.get_or_create(name="model", data_type=STRING, website=harvey_norman, selector=mommy.make(
        Selector, selector_type=TEXT, css_selector=".product-id.meta::text", website=harvey_norman
    ))
    Selector.objects.get_or_create(selector_type=LINK, css_selector=".product-info a", website=harvey_norman)
    Selector.objects.get_or_create(selector_type=PAGINATION, css_selector="li a.next", website=harvey_norman)


@transaction.atomic()
def run():
    set_up_websites()
