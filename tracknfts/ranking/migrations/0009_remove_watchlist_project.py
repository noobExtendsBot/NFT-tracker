# Generated by Django 3.2.12 on 2022-04-13 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ranking', '0008_watchlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='project',
        ),
    ]
