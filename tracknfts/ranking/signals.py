from django.db.models.signals import post_save
from django.dispatch import receiver

import logging

from .models import Project
from .tasks import get_ranking_data

logger = logging.getLogger("django")


@receiver(post_save, sender=Project)
def get_task_running(sender, instance, created, **kwargs):
    """
    fetch data for Ranking table with the help of a cronjob, whenever a new project is saved
    """
    if created:
        logger.info(instance.id)
        get_ranking_data.delay(instance.id)
    # get_ranking_data.delay(instance.id)
