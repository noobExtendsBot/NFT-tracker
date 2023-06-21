from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, UUIDField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for TrackNFTs.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    uid = UUIDField(default=uuid4, unique=True, editable=False, max_length=36)
    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


COMMUNITY_CHOICES = [
    ("twitter", "twitter"),
    ("discord", "discord"),
]


class AlertConfig(models.Model):
    days = models.IntegerField()
    rate = models.DecimalField(max_digits=30, decimal_places=15)
    community = models.CharField(max_length=30, choices=COMMUNITY_CHOICES)

    def __str__(self):
        return f"{self.community, self.days , self.rate}"


class AlertSystem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_alert")
    config = models.ForeignKey(AlertConfig, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email, self.config.community, self.config.rate}"
