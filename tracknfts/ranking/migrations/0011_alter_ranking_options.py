# Generated by Django 3.2.12 on 2022-04-15 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ranking', '0010_watchlist_project'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('-discord_growth_rate',)},
        ),
    ]