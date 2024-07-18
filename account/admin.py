from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from account.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)


admin.site.unregister(Group)
