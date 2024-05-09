# Generated by Django 4.2.11 on 2024-05-09 07:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0033_productreview_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='off_percent',
            field=models.PositiveBigIntegerField(validators=[django.core.validators.MinValueValidator(70)]),
        ),
    ]
