from django.db import models
from django.utils import timezone

from user.models import User


class MoneyLogs(models.Model):
    class OperationEnum(models.TextChoices):
        REPLENISHMENT = "REPLENISHMENT"
        LOAN = "LOAN"
        WITHDRAWAL = "WITHDRAWAL"

    borrower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="borrower")
    source = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="source")
    operation = models.CharField(choices=OperationEnum.choices, max_length=255)
    sum = models.FloatField()
    date = models.DateField(default=timezone.now)
