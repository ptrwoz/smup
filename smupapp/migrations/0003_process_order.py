# Generated by Django 3.2.9 on 2022-01-28 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smupapp', '0002_unit_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='order',
            field=models.IntegerField(default=-1),
        ),
    ]