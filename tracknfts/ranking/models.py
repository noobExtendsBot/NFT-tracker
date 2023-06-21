import uuid
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


def get_image_path(instance, filename):
    return f"{instance.name}/{filename}"


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to=get_image_path, default="default.jpg")
    website_link = models.URLField(max_length=2000)
    twitter_link = models.URLField(max_length=2000)
    discord_link = models.URLField(max_length=2000)
    opensea_link = models.URLField(max_length=2000)
    description = models.TextField(max_length=2000)

    def __str__(self):
        return self.name


class Twitter(models.Model):
    twitter_user_id = models.CharField(max_length=100)
    twitter_followers_count = models.CharField(max_length=200)
    twitter_growth_rate = models.DecimalField(
        max_digits=30, decimal_places=15, blank=True, null=True
    )
    twitter_engagement_rate = models.DecimalField(
        max_digits=30, decimal_places=15, blank=True, null=True
    )

    class Meta:
        abstract = True


class Discord(models.Model):
    discord_followers_count = models.CharField(max_length=200)
    discord_growth_rate = models.DecimalField(
        max_digits=30, decimal_places=15, blank=True, null=True
    )

    class Meta:
        abstract = True


class Ranking(Twitter, Discord):
    """
    Ranking table extends Twitter and Discord table
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.project.name


class TwitterFollowersRecord(models.Model):
    """
    Maintain followers record of Twitter for calculating moving average for growth rate
    """

    ranking_id = models.ForeignKey(Ranking, on_delete=models.CASCADE)
    followers_count = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ranking_id.project.name


class DiscordFollowersRecord(models.Model):
    """
    Maintain followers record of Discord for calculating moving average for growth rate
    """

    ranking_id = models.ForeignKey(Ranking, on_delete=models.CASCADE)
    followers_count = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ranking_id.project.name


class WatchList(models.Model):
    """
    Project added to user watch list
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_watchlist"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_watchlist",
        blank=True,
        null=True,
    )  # TODO remove blank and null

    def __str__(self):
        return f"{self.user.email}"
