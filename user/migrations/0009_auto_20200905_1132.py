# Generated by Django 3.1 on 2020-09-05 11:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20200905_1125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_pic',
        ),
        migrations.AlterField(
            model_name='user',
            name='confirm_code',
            field=models.UUIDField(default=uuid.UUID('e6237de6-4f8c-4142-ae0b-5674780d1047'), editable=False),
        ),
    ]
