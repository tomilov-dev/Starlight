from django.contrib import admin

from .models import (
    IMDb,
    TMDb,
    Genre,
    MovieGenre,
    Collection,
    Country,
    MovieCountry,
    ProductionCompany,
    MovieProduction,
)


@admin.register(IMDb)
class IMDbAdmin(admin.ModelAdmin):
    list_display = ["imdb_mvid", "title_en", "title_ru"]
    readonly_fields = ["imdb_mvid"]

    search_fields = ["title_en", "title_ru"]


@admin.register(TMDb)
class TMDbAdmin(admin.ModelAdmin):
    list_display = ["imdb_mvid"]
    readonly_fields = ["imdb_mvid"]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(MovieGenre)
class MovieGenreAdmin(admin.ModelAdmin):
    list_display = ["imdb_mvid", "genre"]
    readonly_fields = ["imdb_mvid"]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(MovieCountry)
class MovieCountryAdmin(admin.ModelAdmin):
    list_display = ["imdb_mvid", "country"]
    readonly_fields = ["imdb_mvid"]


@admin.register(ProductionCompany)
class ProductionCompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(MovieProduction)
class MovieProductionAdmin(admin.ModelAdmin):
    pass
