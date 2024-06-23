"""Content types according IMDb"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from services.models import MovieTypeSDM


movie_types: list[MovieTypeSDM] = [
    MovieTypeSDM(
        imdb_name=d[0],
        name_en=d[1],
        name_ru=d[2],
    )
    for d in [
        ("movie", "Movie", "Фильм"),
        ("short", "Short Movie", "Короткометражка"),
        ("tvEpisode", "TV Episode", "Телевизионный эпизод"),
        ("tvMiniSeries", "TV Mini Series", "Телевизионный мини-сериал"),
        ("tvMovie", "TV Movie", "Телевизионный фильм"),
        ("tvSeries", "TV Series", "Телевизионный сериал"),
        ("tvShort", "TV Short", "Телевизионная короткометражка"),
        ("tvSpecial", "TV Special", "Телевизионный спецвыпуск"),
        ("video", "Video", "Видео"),
        ("videoGame", "Video Game", "Видео-игра"),
    ]
]
