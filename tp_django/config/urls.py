from django.urls import include, path

urlpatterns = [
    path("api/boutique/", include("boutique.urls")),
    path("api/formation/", include("formation.urls")),
]
