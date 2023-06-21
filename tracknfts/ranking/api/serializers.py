from rest_framework import serializers

from tracknfts.ranking.models import (
    DiscordFollowersRecord,
    Project,
    Ranking,
    TwitterFollowersRecord,
    WatchList,
)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class RankingSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(read_only=True, source="project.id")
    name = serializers.CharField(read_only=True, source="project.name")

    class Meta:
        model = Ranking
        fields = (
            "project_id",
            "name",
            "twitter_followers_count",
            "discord_followers_count",
            "twitter_growth_rate",
            "discord_growth_rate",
            "twitter_engagement_rate",
        )


class AddToWatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchList
        fields = "__all__"


class WatchListSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta:
        model = WatchList
        fields = ("project",)


class TwitterFollowersRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterFollowersRecord
        fields = ("followers_count", "date")


class DiscordFollowersRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordFollowersRecord
        fields = ("followers_count", "date")


class AnalyticsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = (
            "twitter_engagement_rate",
            "twitter_growth_rate",
            "discord_followers_count",
            "discord_growth_rate",
        )
