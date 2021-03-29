from django.contrib.auth.models import User
from model_mommy import mommy

from cms.accounts.models import Company, Team


def run():
    company, _ = Company.objects.get_or_create(name="Test Company")
    user: User = User.objects.create_user("test", password="password")
    user.profile.company = company
    user.save()
    mommy.make(Team, name="test team", company=company, users=[user])
