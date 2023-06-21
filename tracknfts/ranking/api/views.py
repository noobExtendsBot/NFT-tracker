import logging

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tracknfts.ranking.models import (
    DiscordFollowersRecord,
    Project,
    Ranking,
    TwitterFollowersRecord,
    WatchList,
)

from .serializers import (
    AddToWatchListSerializer,
    AnalyticsDataSerializer,
    DiscordFollowersRecordSerializer,
    ProjectSerializer,
    RankingSerializer,
    TwitterFollowersRecordSerializer,
)

logger = logging.getLogger("django")


class ProjectDetailView(APIView):
    """
    get detail of a project pk (uuid)
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
            serializer = ProjectSerializer(project)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Project.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data=["Resource not found"]
            )


class RankingListView(ListAPIView):
    """
    get Ranking model
    """

    permission_classes = ()
    serializer_class = RankingSerializer
    queryset = Ranking.objects.all().order_by("-discord_growth_rate")


class WatchListSerializerView(APIView):
    """
    List Ranking of Projects in User's WatchList
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = RankingSerializer

    def get(self, request):
        try:
            watchlist_projects = WatchList.objects.filter(
                user=self.request.user
            ).values_list("project__id", flat=True)
            watchlist_projects = [str(data) for data in watchlist_projects]
            ranking_obj = Ranking.objects.filter(
                project__id__in=watchlist_projects
            ).order_by("-discord_growth_rate")
            serializer = RankingSerializer(ranking_obj, many=True)
            # data = [data['ranking'] for data in serializer.data]
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except WatchList.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data=["Resource not found"]
            )


class AddToWatchList(APIView):
    """
    Add a project to user WatchList
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AddToWatchListSerializer

    def post(self, request, pk):
        try:
            if WatchList.objects.filter(
                user=self.request.user, project__id=pk
            ).exists():
                return Response(
                    status=status.HTTP_409_CONFLICT, data=["Resource already exists"]
                )
            else:
                project_obj = Project.objects.get(id=pk)
                watchlist_obj = WatchList.objects.create(
                    user=self.request.user, project=project_obj
                )
                serializer = AddToWatchListSerializer(watchlist_obj)
                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        except Project.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data=["Resource does not exist"]
            )


class AnalyticsView(APIView):
    """
    get Twitter and Discord records for a particular project
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            twitter_records = TwitterFollowersRecord.objects.filter(
                ranking_id__project__id=pk
            ).order_by("-date")
            twitter_serializer = TwitterFollowersRecordSerializer(
                twitter_records, many=True
            )
            discord_records = DiscordFollowersRecord.objects.filter(
                ranking_id__project__id=pk
            ).order_by("-date")
            discord_serializer = DiscordFollowersRecordSerializer(
                discord_records, many=True
            )
            analytics_data = Ranking.objects.get(project__id=pk)
            analytics_serializer = AnalyticsDataSerializer(analytics_data)
            data = {
                "twitter_records": twitter_serializer.data,
                "discord_records": discord_serializer.data,
                "twitter_engagement_rate": analytics_serializer.data[
                    "twitter_engagement_rate"
                ],
                "twitter_growth_rate": analytics_serializer.data["twitter_growth_rate"],
                "discord_followers_count": analytics_serializer.data[
                    "discord_followers_count"
                ],
                "discord_growth_rate": analytics_serializer.data["discord_growth_rate"],
            }
            return Response(status=status.HTTP_200_OK, data=data)
        except (
            TwitterFollowersRecord.DoesNotExist,
            DiscordFollowersRecord.DoesNotExist,
            Ranking.DoesNotExist,
        ):
            return Response(
                status=status.HTTP_404_NOT_FOUND, data=["Resource not found"]
            )
