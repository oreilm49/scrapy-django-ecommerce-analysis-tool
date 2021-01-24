from cms.constants import CATEGORY
from cms.models import Website, Category, Url


def set_up_websites():
    harvey_norman, _ = Website.objects.get_or_create(name="harvey_norman", domain="harveynorman.ie")
    laundry, _ = Category.objects.get_or_create(name="laundry")
    washing_machines, _ = Category.objects.get_or_create(name="washing machines", parent=laundry, alternate_names=["washers", "front loaders"])
    Url.objects.get_or_create(url="https://www.harveynorman.ie/home-appliances/appliances/washing-machines/", url_type=CATEGORY, website=harvey_norman, category=washing_machines)
