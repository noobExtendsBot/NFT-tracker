import logging

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from tracknfts.users.models import AlertConfig, AlertSystem

from .serializers import AlertConfigSerializer, AlertSystemSerializer, UserSerializer

User = get_user_model()
logger = logging.getLogger("django")


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class UserAlertSystemView(CreateAPIView, DestroyAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = AlertSystemSerializer

    def post(self, validated_data):
        """
        Create user record in AlertSystem
        """
        days, rate, community = (
            self.request.data["days"],
            self.request.data["rate"],
            self.request.data["community"],
        )
        try:
            config_obj = AlertConfig.objects.get(
                days=days, rate=rate, community=community
            )
        except AlertConfig.DoesNotExist:
            config_obj = AlertConfig.objects.create(
                days=days, rate=rate, community=community
            )
            config_obj.save()
        config_data = {
            "days": config_obj.days,
            "rate": config_obj.rate,
            "community": config_obj.community,
        }
        config_serializer = AlertConfigSerializer(data=config_data)
        if config_serializer.is_valid():
            try:
                AlertSystem.objects.get(config=config_obj, user=self.request.user)
                return Response(
                    status=status.HTTP_409_CONFLICT, data=["Resource already exists"]
                )
            except AlertSystem.DoesNotExist:
                new_alert = AlertSystem.objects.create(
                    config=config_obj, user=self.request.user
                )
                serializer = self.get_serializer(new_alert)
                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=config_serializer.errors
            )

    def get(self, validated_data):
        try:
            alerts = AlertSystem.objects.all()
            alerts_serialized = self.get_serializer(alerts, many=True)
        except AlertSystem.DoesNotExist:
            alerts_serialized = {"data": []}
        return Response(status=status.HTTP_200_OK, data=alerts_serialized.data)

    def delete(self, request, pk=None):
        """
        Delete user record in AlertSystem
        """
        days, rate, community = (
            self.request.data["days"],
            self.request.data["rate"],
            self.request.data["community"],
        )
        try:
            config_obj = AlertConfig.objects.get(
                days=days, rate=rate, community=community
            )
        except AlertConfig.DoesNotExist:
            config_obj = AlertConfig.objects.create(
                days=days, rate=rate, community=community
            )
            config_obj.save()
        config_data = {
            "days": config_obj.days,
            "rate": config_obj.rate,
            "community": config_obj.community,
        }
        config_serializer = AlertConfigSerializer(data=config_data)
        if config_serializer.is_valid():
            # data = {"config": config_serializer.data, "user": self.request.user.id}
            try:
                alert_obj = AlertSystem.objects.get(
                    config=config_obj, user=self.request.user
                )
                alert_obj.delete()
                return Response(status=status.HTTP_200_OK, data=["Resource removed"])
            except AlertSystem.DoesNotExist:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST, data=["No resource to delete"]
                )
        else:
            logger.info("error in config_serializer")
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=config_serializer.errors
            )
