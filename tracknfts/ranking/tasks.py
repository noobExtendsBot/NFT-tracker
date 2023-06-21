import logging
import time

import environ
from django.conf import settings
from django.core.mail import send_mail

from config import celery_app
from tracknfts.users.models import AlertSystem

from .models import (
    DiscordFollowersRecord,
    Project,
    Ranking,
    TwitterFollowersRecord,
    WatchList,
)
from .utils import (
    api,
    client,
    get_discord_followers_count,
    get_likes_by_user,
    get_running_average,
    get_twitter_followers_count,
    get_twitter_userid,
    get_user_tweets,
)

logger = logging.getLogger("django")
env = environ.Env()


@celery_app.task()
def get_ranking_data(project_id):
    """
    celery job fetch data for Ranking model and create a new record
    """
    time.sleep(5)
    project_obj = Project.objects.get(id=project_id)
    twitter_username = project_obj.twitter_link.rsplit("/", 1)[-1]
    discord_url = project_obj.discord_link
    user_id = get_twitter_userid(api, twitter_username)
    twitter_followers_count = get_twitter_followers_count(api, user_id)
    discord_followers_count = get_discord_followers_count(discord_url)
    # sum of last 5 liked
    liked_tweet_sum = get_likes_by_user(client, user_id)
    # tweet, retweet, and comment total likes
    remaning_tweet_sum = get_user_tweets(client, user_id)
    twitter_engagement_rate = (
        (liked_tweet_sum + remaning_tweet_sum / 20) / twitter_followers_count
    ) * 100
    try:
        ranking_obj = Ranking.objects.create(
            project=project_obj,
            twitter_user_id=user_id,
            twitter_followers_count=twitter_followers_count,
            twitter_growth_rate=0,
            twitter_engagement_rate=twitter_engagement_rate,
            discord_followers_count=discord_followers_count,
            discord_growth_rate=0,
        )
        ranking_obj.save()
    except Exception as e:
        raise e


@celery_app.task()
def get_and_set_twitter_followers():
    """
    A celery job to run daily, in order to fetch Twitter followers record for all Projects in Ranking Table
    """
    ranking_objects = Ranking.objects.all()
    for item in ranking_objects:
        twitter_followers_count = get_twitter_followers_count(api, item.twitter_user_id)
        twitter_record = TwitterFollowersRecord.objects.create(
            ranking_id=item, followers_count=twitter_followers_count
        )
        twitter_record.save()


@celery_app.task()
def get_and_set_discord_followers():
    """
    A celery job to run daily, in order to fetch Discord followers record for all Projects in Ranking Table
    """
    ranking_objects = Ranking.objects.all()
    for item in ranking_objects:
        discord_url = item.project.discord_link
        try:
            followers_count = get_discord_followers_count(discord_url)
            discord_record = DiscordFollowersRecord.objects.create(
                ranking_id=item, followers_count=followers_count
            )
            discord_record.save()

        except Exception as e:
            raise e


@celery_app.task()
def update_twitter_ranking_model():
    """
    calculate twitter growth rate if >=7 record in TwitterFollowersRecord table
    """
    # store project name and growth_rate [[project_id, growth_rate]]
    ranking_obj = Ranking.objects.all()
    for proj in ranking_obj:
        # get calculate engagement rate
        twitter_username = proj.project.twitter_link.rsplit("/", 1)[-1]
        user_id = get_twitter_userid(api, twitter_username)
        # sum of last 5 liked
        liked_tweet_sum = get_likes_by_user(client, user_id)
        # tweet, retweet, and comment total likes
        remaning_tweet_sum = get_user_tweets(client, user_id)
        logger.info("info for engagement rate gathered")
        # calculate growth rate
        followers_obj = TwitterFollowersRecord.objects.filter(ranking_id=proj).order_by(
            "-date"
        )[:7]
        if followers_obj.exists():
            twitter_followers_count = int(followers_obj[0].followers_count)
        else:
            twitter_followers_count = get_twitter_followers_count(api, user_id)

        if len(followers_obj) < 7:
            growth_rate = 0
        else:
            followers_list = [int(data.followers_count) for data in followers_obj]
            growth_rate = (
                (twitter_followers_count - get_running_average(followers_list))
                / twitter_followers_count
            ) * 100
        logger.info("growth rate calculated")
        # calculate engagement rate
        twitter_engagement_rate = (
            (liked_tweet_sum + remaning_tweet_sum / 20) / twitter_followers_count
        ) * 100
        proj.twitter_followers_count = twitter_followers_count
        proj.twitter_growth_rate = growth_rate
        proj.twitter_engagement_rate = twitter_engagement_rate
        proj.save()
        # invoke celery to send mail
        notify_user_twitter.s(proj.project.id, growth_rate).delay()


@celery_app.task()
def update_discord_ranking_model():
    """
    calculate twitter growth rate if >=7 record in DiscordFollowersRecord table
    """
    ranking_obj = Ranking.objects.all()
    for proj in ranking_obj:
        discord_url = proj.project.discord_link
        followers_obj = DiscordFollowersRecord.objects.filter(ranking_id=proj).order_by(
            "-date"
        )[:7]
        if followers_obj.exists():
            discord_followers_count = int(followers_obj[0].followers_count)
        else:
            discord_followers_count = get_discord_followers_count(discord_url)

        if len(followers_obj) < 7:
            growth_rate = 0
        else:
            followers_list = [int(data.followers_count) for data in followers_obj]
            growth_rate = (
                (discord_followers_count - get_running_average(followers_list))
                / discord_followers_count
            ) * 100
        logger.info(f"{growth_rate} for Discord")
        proj.discord_followers_count = discord_followers_count
        proj.discord_growth_rate = growth_rate
        proj.save()
        # invoke celery to send mail
        notify_user_discord.s(proj.project.id, growth_rate).delay()
    logger.info("updated the ranking model for discord")


@celery_app.task()
def notify_user_twitter(project_id, rate):
    # dict should be wailist_user["someemail@gmail.com"] = project_id
    watchlist_obj = WatchList.objects.all()
    watchlist_users = dict()
    watchlist_users = {data.user.email: str(data.project.id) for data in watchlist_obj}
    # prepare email data
    project_name = Project.objects.values("name").get(id=project_id)
    subject = f"Notification for {project_name['name']}'s Twitter growth"
    message = f"{project_name['name']} showed a rate of {rate}"
    recipient_list = []
    email_from = settings.EMAIL_HOST
    logger.info(float(rate))
    if float(rate) > 20:
        # email when rate > 20%
        alert_obj = AlertSystem.objects.filter(
            config__rate=20, config__community="twitter"
        )
        for data in alert_obj:
            # check if user has added the project to watchlist
            if (
                watchlist_users[data.user.email]
                and watchlist_users[data.user.email] == project_id
            ):
                recipient_list.append(data.user.email)
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            raise e
    elif float(rate) < -10:
        # email when rate < -10%
        alert_obj = AlertSystem.objects.filter(
            config__rate=-10, config__community="twitter"
        )
        for data in alert_obj:
            if (
                watchlist_users[data.user.email]
                and watchlist_users[data.user.email] == project_id
            ):
                recipient_list.append(data.user.email)
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            raise e


@celery_app.task()
def notify_user_discord(project_id, rate):
    # dict should be wailist_user["someemail@gmail.com"] = project_id
    watchlist_obj = WatchList.objects.all()
    watchlist_users = dict()
    watchlist_users = {data.user.email: str(data.project.id) for data in watchlist_obj}
    # prepare email data
    project_name = Project.objects.values("name").get(id=project_id)
    subject = f"Notification for {project_name['name']}'s Discord growth"
    message = f"{project_name['name']} showed a rate of {rate}"
    recipient_list = []
    email_from = settings.EMAIL_HOST
    logger.info(float(rate))
    if float(rate) > 20:
        # email when rate > 20%
        alert_obj = AlertSystem.objects.filter(
            config__rate=20, config__community="discord"
        )
        for data in alert_obj:
            # check if user has added the project to watchlist
            if (
                watchlist_users[data.user.email]
                and watchlist_users[data.user.email] == project_id
            ):
                recipient_list.append(data.user.email)
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            raise e
    elif float(rate) < -10:
        # email when rate < -10%
        alert_obj = AlertSystem.objects.filter(
            config__rate=-10, config__community="discord"
        )
        for data in alert_obj:
            if (
                watchlist_users[data.user.email]
                and watchlist_users[data.user.email] == project_id
            ):
                recipient_list.append(data.user.email)
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            raise e
