import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.utils import timezone


def extract_file_extension(filename):
    return filename.split('.')[1]


def upload_img_file(instance, filename: str) -> str:
    user_id = getattr(instance, 'id', None)

    new_filename = '.'.join((str(uuid.uuid4()), extract_file_extension(filename)))
    return f'users/{user_id}/{new_filename}'


class Passport(models.Model):
    series = models.CharField(max_length=4)
    number = models.CharField(max_length=6)
    who = models.TextField()
    code_who = models.CharField(max_length=10)
    when = models.DateField()


class User(AbstractUser):
    class StateEnum(models.TextChoices):
        CONFIRMED = "CONFIRMED"
        NOT_CONFIRMED = "NOT_CONFIRMED"

    phone_number = models.CharField(max_length=12, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    fathers_name = models.CharField(max_length=255)
    credit_card_number = models.CharField(max_length=16, blank=True, null=True)
    passport = models.ForeignKey(Passport, on_delete=models.CASCADE, null=True, blank=True)
    is_confirmed = models.CharField(max_length=255,
                                    choices=StateEnum.choices, default=StateEnum.NOT_CONFIRMED)
    balance = models.FloatField(default=0)
    vk_link = models.URLField(null=True, blank=True, default='')
    instagram_link = models.URLField(null=True, blank=True, default='')

    @property
    def follower_items(self):
        return Follow.objects.filter(follow_user=self)

    @property
    def follow_items(self):
        return Follow.objects.filter(follower=self)

    @property
    def borrowers(self):
        return User.objects.filter(id__in=(self.follower_items.values_list("follower")))

    @property
    def follows(self):
        return User.objects.filter(
            id__in=(self.follow_items.values_list("follow_user")))

    @property
    def has_current_debts(self):
        return len(MoneyLogs.objects.filter(destination=self, is_active=True)) > 0

    def has_passport(self):
        if self.passport:
            return True
        else:
            return False

    def return_debt(self):
        if self.can_pay_debt:
            transactions = MoneyLogs.objects.filter(destination=self, is_active=True)
            sum = transactions.aggregate(Sum('sum'))['sum__sum']
            for transaction in transactions:
                if transaction.operation == "LOAN":
                    transaction.source.balance += transaction.sum + (transaction.sum * 200 / sum)
                    transaction.source.save()
                    self.balance -= transaction.sum + (transaction.sum * 200 / sum)
                    self.save()
                    MoneyLogs.objects.create(source=self, destination=transaction.source, operation="WITHDRAWAL",
                                             sum=transaction.sum + (transaction.sum * 200 / sum), is_active=False)

                transaction.is_active = False
                transaction.save()
            return True
        else:
            return False

    @property
    def can_pay_debt(self):
        transactions = MoneyLogs.objects.filter(destination=self, is_active=True)
        sum = transactions.aggregate(Sum('sum'))['sum__sum']
        if sum is None:
            sum = 0
        return self.balance - sum >= 1E-8

    # @property
    # def friends(self):
    #     return User.objects.filter(
    #         id__in=(self.followers.values_list("follower") and self.follows.values_list("follow_user")))

    class Meta:
        db_table = 'site_user'


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    follow_user = models.ForeignKey(User, related_name='follow_user', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class MoneyLogs(models.Model):
    class OperationEnum(models.TextChoices):
        REPLENISHMENT = "REPLENISHMENT"
        LOAN = "LOAN"
        WITHDRAWAL = "WITHDRAWAL"

    destination = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="borrower")
    source = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="source")
    operation = models.CharField(choices=OperationEnum.choices, max_length=255)
    sum = models.FloatField()
    date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)