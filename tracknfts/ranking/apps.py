from django.apps import AppConfig
from django.core.signals import request_finished


class RankingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tracknfts.ranking"

    def ready(self):
        # to make sure signals works (refer doc)
        from . import signals
