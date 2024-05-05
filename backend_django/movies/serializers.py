from rest_framework import serializers

from .models import IMDb, TMDb, Genre, MovieGenre, Country, MovieCountry


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class MovieCountrySerializer(serializers.ModelSerializer):
    name = CountrySerializer()

    class Meta:
        model = MovieCountry
        fields = ["name"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class MovieGenreSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()

    class Meta:
        model = MovieGenre
        fields = ["genre"]


class IMDbSerializer(serializers.ModelSerializer):
    genres = MovieGenreSerializer(many=True)
    countries = MovieCountrySerializer(many=True)

    class Meta:
        model = IMDb
        fields = [
            "imdb_mvid",
            "type",
            "title_en",
            "title_ru",
            "is_adult",
            "runtime",
            "rate",
            "wrate",
            "votes",
            "genres",
            "countries",
        ]


class TMDbSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMDb
        fields = [
            "tmdb_mvid",
            "collection",
            "release_date",
            "budget",
            "revenue",
            "tagline_en",
            "overview_en",
            "tagline_ru",
            "overview_ru",
            "rate",
            "votes",
            "popularity",
        ]
