from django.contrib.auth.models import User
from django.test import TestCase

from cms.accounts.models import Company, Team
from cms.accounts.scripts.load_accounts import load_accounts


class TestScripts(TestCase):

    def test_load_accounts(self):
        load_accounts()
        company: Company = Company.objects.get(name="Test Company")
        user: User = User.objects.get(username="test")
        self.assertEqual(user.profile.company, company)
        self.assertTrue(Team.objects.filter(name="test team", company=company, users__in=[user]))
