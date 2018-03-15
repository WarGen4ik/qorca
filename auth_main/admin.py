from django.contrib import admin

from auth_main.models import User, Profile

admin.site.register(User)
admin.site.register(Profile)