from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CharField

from tracknfts.ranking.api.serializers import WatchListSerializer
from tracknfts.users.models import AlertConfig, AlertSystem

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = CharField(source="username")
    watchlists = WatchListSerializer(many=True, source="user_watchlist")

    class Meta:
        model = User
        fields = ["uid", "email", "name", "watchlists"]
        read_only_fields = ["uid", "email"]
        lookup_field = "uid"


class AlertConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertConfig
        fields = ["days", "rate", "community"]


class AlertSystemSerializer(serializers.ModelSerializer):
    config = AlertConfigSerializer()

    class Meta:
        model = AlertSystem
        fields = ["config"]
