# Generated by Django 3.1 on 2020-08-17 08:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='confirm_code',
            field=models.UUIDField(default=uuid.UUID('f394b954-3891-4cde-97f2-0b73551f03f8'), editable=False),
        ),
    ]
