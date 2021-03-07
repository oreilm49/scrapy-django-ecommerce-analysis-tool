from django.contrib.auth.models import User, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from cms.constants import MAX_LENGTH
from cms.models import BaseModel


class Company(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The company name"), unique=True)


class Profile(BaseModel):
    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, verbose_name=_('Company'), on_delete=models.CASCADE, null=True)


@receiver(post_save, sender=User)
def user_profile_saved(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class Team(BaseModel):
    name = models.CharField(verbose_name=_("Name"), max_length=MAX_LENGTH, help_text=_("The company name"), unique=True)
    company = models.ForeignKey(Company, verbose_name=_('Company'), on_delete=models.CASCADE)
    users = models.ManyToManyField(User, verbose_name=_("Users"))
    permissions = models.ManyToManyField(Permission, verbose_name=_("Permissions"))
