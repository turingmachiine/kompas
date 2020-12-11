from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from info.models import MoneyLogs
from user.models import User, Passport, Follow


def return_money(modeladmin, request, queryset):
    for obj in queryset:
        transactions = MoneyLogs.objects.filter(destination=obj)
        for transaction in transactions:
            if transaction.operation == "COMMISSION":
                obj.balance -= transaction.sum
                obj.save()
                MoneyLogs.objects.create(source=obj, operation="WITHDRAWAL", sum=transaction.sum)
            elif transaction.operation == "LOAN":
                transaction.source.balance += transaction.sum
                transaction.source.save()
                obj.balance -= transaction.sum
                obj.save()
                MoneyLogs.objects.create(source=obj, destination=transaction.source,  operation="WITHDRAWAL", sum=transaction.sum)



@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ['username', 'email', 'balance', 'is_confirmed']
    list_filter = ['is_confirmed']
    actions = [return_money]

admin.site.register(Passport)
admin.site.register(Follow)
