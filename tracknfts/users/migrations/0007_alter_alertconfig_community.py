# Generated by Django 3.2.12 on 2022-04-15 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_alertsystem_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertconfig',
            name='community',
            field=models.CharField(choices=[('twitter', 'twitter'), ('discord', 'discord')], max_length=30),
        ),
    ]