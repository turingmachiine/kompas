# Generated by Django 3.1 on 2020-10-07 13:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MoneyLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.CharField(choices=[('REPLENISHMENT', 'Replenishment'), ('LOAN', 'Loan'), ('WITHDRAWAL', 'Withdrawal')], max_length=255)),
                ('sum', models.FloatField()),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('borrower', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='borrower', to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='source', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
