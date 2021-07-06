from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer
from django.contrib.auth import get_user_model
from .serializers import ChangePasswordSerializer
User = get_user_model()


class RegisterUserView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterUserSerializer
    queryset = ''


class ChangePasswordView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
