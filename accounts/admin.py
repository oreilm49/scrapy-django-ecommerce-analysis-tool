from django.contrib import admin

from accounts.models import Profile, Company, Team


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'company',


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = 'id', 'name',


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'company',
