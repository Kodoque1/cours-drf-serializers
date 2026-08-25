from rest_framework import generics

from .models import Booking, Order
from .serializers import (
    BookingSerializer,
    OrderHyperlinkedSerializer,
    OrderSerializer,
    SignupSerializer,
    UserProfileSerializer,
)
from django.contrib.auth.models import User


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderHyperlinkedSerializer
