# Generated by Django 4.2.11 on 2024-04-16 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0006_rename_alternative_mobile_useraddress_alt_mobile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraddress',
            old_name='zip_code',
            new_name='zipcode',
        ),
    ]
