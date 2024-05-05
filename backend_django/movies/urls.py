from django.contrib import admin
from django.urls import path

from .views import get_movie, get_genres_list, get_genre

urlpatterns = [
    path("api/movie/<slug:slug>/", get_movie, name="get_movie"),
    path("api/genres_list/", get_genres_list, name="get_genres_list"),
    path("api/genre/<slug:slug>/", get_genre, name="get_genre"),
]
