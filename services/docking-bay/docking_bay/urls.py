"""URL configuration for the Death Star Docking Bay service."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/docking/", include("docking.urls")),
]
