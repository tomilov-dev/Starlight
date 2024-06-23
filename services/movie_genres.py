"""Genre Types from IMDb & TMDb"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from services.models import GenreSDM


genres: list[GenreSDM] = [
    GenreSDM(
        name_en=d[0],
        slug=d[1],
        tmdb_name=d[2],
        name_ru=d[3],
    )
    for d in [
        ("Short", "short", None, "Короткий фильм"),
        ("Talk-Show", "talk-show", None, "Разговорное шоу"),
        ("Adult", "adult", None, "Для взрослых"),
        ("Game-Show", "game-show", None, "Игровое шоу"),
        ("Reality-TV", "reality-tv", None, "Реалити шоу"),
        ("News", "news", None, "Новости"),
        ("Horror", "horror", "Horror", "Ужасы"),
        ("Musical", "musical", None, "Мьюзикл"),
        ("Sport", "sport", None, "Спорт"),
        ("Documentary", "documentary", "Documentary", "Документальное кино"),
        ("Music", "music", "Music", "Музыкальный фильм"),
        ("Western", "western", "Western", "Вестерн"),
        ("Comedy", "comedy", "Comedy", "Комедия"),
        ("Animation", "animation", "Animation", "Мультфильм"),
        ("Family", "family", "Family", "Семейное кино"),
        ("Fantasy", "fantasy", "Fantasy", "Фэнтези"),
        ("War", "war", "War", "Военный"),
        ("Thriller", "thriller", "Thriller", "Триллер"),
        ("Mystery", "mystery", "Mystery", "Мистика"),
        ("Romance", "romance", "Romance", "Романтика"),
        ("Sci-Fi", "sci-fi", "Science Fiction", "Фантастика"),
        ("Biography", "biography", None, "Биография"),
        ("History", "history", "History", "Исторический"),
        ("Adventure", "adventure", "Adventure", "Приключения"),
        ("Action", "action", "Action", "Экшен"),
        ("Crime", "crime", "Crime", "Криминал"),
        ("Drama", "drama", "Drama", "Драма"),
    ]
]
