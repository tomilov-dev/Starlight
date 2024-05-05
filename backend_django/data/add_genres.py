import os
import sys
import django
from pathlib import Path

PROJ_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJ_DIR))
from services.movie_genres import genres

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starlight_backend.settings")
django.setup()

from movies.models import Genre


class GenresAdder(object):
    def add(self) -> None:
        for genre in genres:
            Genre.objects.create(
                imdb_name=genre.imdb,
                slug=genre.slug,
                tmdb_name=genre.tmdb,
                name_ru=genre.name_ru,
            )


if __name__ == "__main__":
    adder = GenresAdder()
    adder.add()
