# Generated by Django 4.2.11 on 2024-04-28 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0027_wishlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='dummy',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
