from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("bookings/", views.BookingCreateView.as_view(), name="booking-create"),
    path("users/<int:pk>/", views.UserProfileView.as_view(), name="user-profile"),
    path("orders/", views.OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
]
