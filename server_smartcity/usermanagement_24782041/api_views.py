from rest_framework import generics, permissions

from .models import CustomUser
from .serializers import CitizenRegisterSerializer


class CitizenRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CitizenRegisterSerializer
    permission_classes = [permissions.AllowAny]