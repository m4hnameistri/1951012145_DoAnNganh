# Generated by Django 3.2.15 on 2023-10-22 09:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_auto_20231022_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='to_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 22, 16, 0, 29, 176887)),
        ),
    ]