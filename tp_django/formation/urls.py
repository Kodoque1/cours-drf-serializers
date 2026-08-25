from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.FormateurSignupView.as_view(), name="formateur-signup"),
    path("creneaux/", views.CreneauCreateView.as_view(), name="creneau-create"),
    path(
        "formateurs/<int:pk>/",
        views.FormateurProfileView.as_view(),
        name="formateur-profile",
    ),
    path("sessions/", views.SessionListCreateView.as_view(), name="session-list"),
    path(
        "sessions/<int:pk>/",
        views.SessionDetailView.as_view(),
        name="session-detail",
    ),
]
