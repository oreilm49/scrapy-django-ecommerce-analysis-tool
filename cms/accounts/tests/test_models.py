from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from cms.accounts.models import Company, Team, Profile


class TestModels(TestCase):

    def test_company_name(self):
        company: Company = mommy.make(Company, name="test name")
        self.assertEqual(str(company), company.name)

    def test_profile_name(self):
        user: User = User.objects.create_user("test name")
        self.assertEqual(str(user.profile), user.username)

    def test_team_name(self):
        team: Team = mommy.make(Team, name="test name")
        self.assertEqual(str(team), team.name)

    def test_user_profile_saved(self):
        self.assertFalse(Profile.objects.exists())
        with self.subTest("profile created"):
            user: User = User.objects.create_user("test name")
            self.assertTrue(Profile.objects.filter(user=user).exists())

        with self.subTest("profile updated"):
            company: Company = mommy.make(Company)
            user.profile.company = company
            user.save()
            self.assertEqual(Profile.objects.get(user=user).company, company)
