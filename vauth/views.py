from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework import permissions

from .serializers import RegisterUserSerializer

class RegisterUserView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterUserSerializer
    queryset = ''