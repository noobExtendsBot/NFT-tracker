from django.contrib import admin
from .models import (
    Project,
    Ranking,
    TwitterFollowersRecord,
    DiscordFollowersRecord,
    WatchList,
)


admin.site.register(Project)


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "twitter_growth_rate",
        "discord_growth_rate",
    )


@admin.register(TwitterFollowersRecord)
class TwitterFollowersRecordAdmin(admin.ModelAdmin):
    list_display = (
        "ranking_id",
        "followers_count",
        "date",
    )


@admin.register(DiscordFollowersRecord)
class DiscordFollowersRecordAdmin(admin.ModelAdmin):
    list_display = (
        "ranking_id",
        "followers_count",
        "date",
    )


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ("user", "project")
