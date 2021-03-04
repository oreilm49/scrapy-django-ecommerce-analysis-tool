from django.contrib.auth.models import User, Permission
from django.db import models
from django.utils.translation import gettext as _

from cms.constants import MAX_LENGTH
from cms.models import BaseModel


class Company(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The company name"), unique=True)


class Profile(BaseModel):
    user = models.OneToOneField(User, verbose_name=_("Profile"), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, verbose_name=_('Company'), on_delete=models.CASCADE)


class Team(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The company name"), unique=True)
    company = models.ForeignKey(Company, verbose_name=_('Company'), on_delete=models.CASCADE)
    users = models.ManyToManyField(User, verbose_name=_("Users"))
    permissions = models.ManyToManyField(Permission, verbose_name=_("Permissions"))

