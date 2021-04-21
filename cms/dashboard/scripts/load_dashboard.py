from django.contrib.auth.models import User
from django.db import transaction

from cms.dashboard.models import CategoryGapAnalysisReport
from cms.models import Category, Brand


def load_dashboard():
    washers: Category = Category.objects.get(name="washing machines")
    admin: User = User.objects.get(username="admin")
    CategoryGapAnalysisReport.objects.create(user=admin, name="test", category=washers, brand=Brand.objects.get(name="indesit"))


@transaction.atomic()
def run():
    load_dashboard()
