from rest_framework import generics

from .models import Creneau, Formateur, Session
from .serializers import (
    CreneauSerializer,
    FormateurProfileSerializer,
    FormateurSignupSerializer,
    SessionHyperlinkedSerializer,
    SessionSerializer,
)


class FormateurSignupView(generics.CreateAPIView):
    serializer_class = FormateurSignupSerializer


class CreneauCreateView(generics.CreateAPIView):
    queryset = Creneau.objects.all()
    serializer_class = CreneauSerializer


class FormateurProfileView(generics.RetrieveUpdateAPIView):
    queryset = Formateur.objects.all()
    serializer_class = FormateurProfileSerializer


class SessionListCreateView(generics.ListCreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class SessionDetailView(generics.RetrieveAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionHyperlinkedSerializer
