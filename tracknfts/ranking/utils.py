import requests
import tweepy
from django.conf import settings

# set your BEARER TOKEN
TWITTER_API_BEARER_TOKEN = settings.TWITTER_API_BEARER_TOKEN
auth = tweepy.OAuth2BearerHandler(TWITTER_API_BEARER_TOKEN)
api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token=TWITTER_API_BEARER_TOKEN)


def get_twitter_userid(api, username):
    """
    get twitter userid
    """
    try:
        user_data = api.get_user(screen_name=username)
    except Exception as e:
        raise e
    return user_data.id


def get_twitter_followers_count(api, id):
    """
    get Twitter followers count
    """
    try:
        user_data = api.get_user(id=id)
    except Exception as e:
        raise e
    return int(user_data.followers_count)


def get_likes_by_user(client, userid):
    """
    calc total number of likes on last 5 tweets liked by User
    """
    try:
        user_data = client.get_liked_tweets(
            id=userid, max_results=5, tweet_fields=["public_metrics"]
        )
        # sum likes on the last 5 tweets
        tweet_likes_sum = sum(
            [data.public_metrics["like_count"] for data in user_data.data]
        )
    except Exception as e:
        raise e
    return tweet_likes_sum


def get_user_tweets(client, id):
    """
    # get last 15 tweets by the user
    # get_user_tweets includes retweets, tweets, and comments by the user
    """
    try:
        tweet_info = client.get_users_tweets(
            id=id,
            max_results=15,
            tweet_fields=["public_metrics"],
            expansions=["referenced_tweets.id"],
        )
        tweet_likes_sum = 0
        for data in tweet_info.data:
            if data.referenced_tweets:
                # if retweet then fetch the original tweet and get like_count
                tweet_info = client.get_tweet(
                    id=data.referenced_tweets[0].id, tweet_fields=["public_metrics"]
                )
                tweet_likes_sum += tweet_info.data.public_metrics["like_count"]
            else:
                # if original tweet then just get like_count
                tweet_likes_sum += data.public_metrics["like_count"]
        # print(tweet_likes_sum)
    except Exception as e:
        raise e
    return tweet_likes_sum


def get_running_average(arr):
    """
    simple running average
    """
    return sum(arr) / 7


def get_discord_followers_count(discord_url):
    url = (
        f"https://discord.com/api/v9/invites/{discord_url.rsplit('/', 1)[-1]}?"
        "with_counts=true&with_expiration=true"
    )
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return int(response.json()["approximate_member_count"])
    except Exception as e:
        raise e
