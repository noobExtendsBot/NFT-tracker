from django.urls import path

from tracknfts.ranking.api.views import (
    AddToWatchList,
    AnalyticsView,
    ProjectDetailView,
    RankingListView,
    WatchListSerializerView,
)

app_name = "ranking"

urlpatterns = [
    path("", view=RankingListView.as_view(), name="ranking_list"),
    path("project/<uuid:pk>/", view=ProjectDetailView.as_view(), name="project_detail"),
    path(
        "project/watchlist/<uuid:pk>/",
        view=AddToWatchList.as_view(),
        name="add_to_watchlist",
    ),
    path("watchlist/", view=WatchListSerializerView.as_view(), name="watchlist"),
    path("analytics/<uuid:pk>/", view=AnalyticsView.as_view(), name="analytics_detail"),
]
