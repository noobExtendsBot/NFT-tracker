# Generated by Django 3.2.12 on 2022-04-12 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_alertconfig_community'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertconfig',
            name='days',
            field=models.IntegerField(),
        ),
    ]
