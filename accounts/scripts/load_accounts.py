from model_mommy import mommy

from accounts.models import Company, Profile, Team


def run():
    company, _ = Company.objects.get_or_create(name="Test Company")
    user: Profile = mommy.make(Profile, company=company, user__username="test user")
    mommy.make(Team, name="test team", company=company, users=[user.user])
