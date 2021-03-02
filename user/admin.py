from datetime import datetime, timedelta

from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from user.models import User, Passport, Follow, MoneyLogs


def return_money(model_admin, request, queryset):
    for obj in queryset:
        obj.return_debt()


@admin.register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ['follower', 'follow_user']
    list_filter = ['follower', 'follow_user']


class PassportListFilter(SimpleListFilter):
    title = _("passport")
    parameter_name = 'passport'

    def lookups(self, request, model_admin):
        return [('yes', 'yes'), ('no', 'no')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(passport__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(passport__isnull=True)
        else:
            return queryset.all()


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'fathers_name', 'email', 'balance', 'credit_card_number',
                    'has_passport', 'is_confirmed']
    list_filter = ['is_confirmed', PassportListFilter]
    actions = [return_money]
    ordering = ['username', 'last_name', 'first_name', 'fathers_name', 'balance']

    def save_model(self, request, obj, form, change):
        if obj.pk:
            orig_obj = User.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()


class SubjectListFilter(admin.SimpleListFilter):
    title = _('passport subject')

    parameter_name = 'subject'

    def lookups(self, request, model_admin):
        list_tuple = []
        subjects = set()
        for passport in Passport.objects.all():
            if passport.series[:2] not in subjects:
                subjects.add(passport.series[:2])
                list_tuple.append((passport.series[:2], passport.series[:2]))
        return list_tuple

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(series__startswith=self.value())
        else:
            return queryset.all()


@admin.register(Passport)
class PassportAdmin(ModelAdmin):
    list_display = ['id', 'series', 'number', 'when', 'who', 'code_who']
    list_filter = ['series', SubjectListFilter, 'when']
    date_hierarchy = 'when'
    ordering = ['id']


class LoanReturnFilter(SimpleListFilter):
    title = _('loan return')

    parameter_name = 'loan_return'

    def lookups(self, request, model_admin):
        return [('yes', 'yes'), ('no', 'no')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(
                Q(date__contains=datetime.date(datetime.now() - timedelta(days=30))) & Q(is_active=True))
        elif self.value() == 'no':
            return queryset.exclude(
                Q(date__contains=datetime.date(datetime.now() - timedelta(days=30))) & Q(is_active=True))
        else:
            return queryset.all()


def return_debt(model_admin, request, queryset):
    users = set()
    for log in queryset:
        if log.destination.id not in users:
            users.add(log.destination.id)
            log.destination.return_debt()


def make_inactive(model_admin, request, queryset):
    for log in queryset:
        log.is_active = False
        log.save()


@admin.register(MoneyLogs)
class MoneyLogs(ModelAdmin):
    list_display = ['source', 'destination', 'sum', 'is_active', 'date', 'operation', 'return_date']
    list_filter = ['is_active', LoanReturnFilter, 'date', 'operation', 'source', 'destination']
    actions = [return_debt, make_inactive]
    date_hierarchy = 'date'

    def return_date(self, obj):
        return obj.date + timedelta(days=30)
