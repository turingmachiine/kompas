from django.contrib import admin

# Register your models here.
from user.models import User, Passport, Follow

admin.site.register(User)
admin.site.register(Passport)
admin.site.register(Follow)
