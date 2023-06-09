# Generated by Django 3.2.12 on 2022-04-08 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ranking", "0005_rename_twitter_project_id_ranking_twitter_user_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ranking",
            name="discord_growth_rate",
            field=models.DecimalField(
                blank=True, decimal_places=15, max_digits=30, null=True
            ),
        ),
        migrations.AlterField(
            model_name="ranking",
            name="twitter_engagement_rate",
            field=models.DecimalField(
                blank=True, decimal_places=15, max_digits=30, null=True
            ),
        ),
        migrations.AlterField(
            model_name="ranking",
            name="twitter_growth_rate",
            field=models.DecimalField(
                blank=True, decimal_places=15, max_digits=30, null=True
            ),
        ),
    ]
