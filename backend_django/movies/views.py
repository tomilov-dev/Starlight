from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import IMDb, Genre, MovieGenre
from .serializers import (
    IMDbSerializer,
    TMDbSerializer,
    GenreSerializer,
    MovieGenreSerializer,
)


@api_view(["GET"])
def get_movie(
    request: HttpRequest,
    slug: str,
) -> HttpResponse:
    imdb_data = get_object_or_404(IMDb, slug=slug)
    imdb = IMDbSerializer(imdb_data)

    tmdb_data = imdb_data.tmdb
    tmdb = TMDbSerializer(tmdb_data) if tmdb_data else None

    return Response(
        {
            "imdb": imdb.data,
            "tmdb": tmdb.data,
        }
    )


@cache_page(60 * 60)
@api_view(["GET"])
def get_genres_list(request: HttpRequest) -> HttpResponse:
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_genre(request: HttpRequest, slug: str) -> HttpResponse:
    genre_data = get_object_or_404(Genre, slug=slug)
    genre = GenreSerializer(genre_data)

    # movies_data = IMDb.objects.filter(genre=genre)
    # movies = IMDbSerializer(movies_data)

    return Response(
        {
            "genre": genre.data,
            # "movies": movies.data,
        }
    )
