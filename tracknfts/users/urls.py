from django.urls import path

from tracknfts.users.views import user_detail_view, user_redirect_view, user_update_view

# from dj_rest_auth.views import LoginView, LogoutView


app_name = "users"
urlpatterns = [
    # path("login/", LoginView.as_view(), name="login"),
    # path("logout/", LogoutView.as_view(), name="logout"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
