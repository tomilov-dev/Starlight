"""Genre Types from IMDb & TMDb"""


class GenreObj:
    """Simple wrapper for genres"""

    def __init__(
        self,
        imdb: str,
        slug: str,
        tmdb: str,
        name_ru: str,
    ) -> None:
        self.imdb = imdb
        self.slug = slug
        self.tmdb = tmdb
        self.name_ru = name_ru


genres: list[GenreObj] = [
    GenreObj("Short", "short", None, "Короткий фильм"),
    GenreObj("Talk-Show", "talk-show", None, "Разговорное шоу"),
    GenreObj("Adult", "adult", None, "Для взрослых"),
    GenreObj("Game-Show", "game-show", None, "Игровое шоу"),
    GenreObj("Reality-TV", "reality-tv", None, "Реалити шоу"),
    GenreObj("News", "news", None, "Новости"),
    GenreObj("Horror", "horror", "Horror", "Ужасы"),
    GenreObj("Musical", "musical", None, "Мьюзикл"),
    GenreObj("Sport", "sport", None, "Спорт"),
    GenreObj("Documentary", "documentary", "Documentary", "Документальное кино"),
    GenreObj("Music", "music", "Music", "Музыкальный фильм"),
    GenreObj("Western", "western", "Western", "Вестерн"),
    GenreObj("Comedy", "comedy", "Comedy", "Комедия"),
    GenreObj("Animation", "animation", "Animation", "Мультфильм"),
    GenreObj("Family", "family", "Family", "Семейное кино"),
    GenreObj("Fantasy", "fantasy", "Fantasy", "Фэнтези"),
    GenreObj("War", "war", "War", "Военный"),
    GenreObj("Thriller", "thriller", "Thriller", "Триллер"),
    GenreObj("Mystery", "mystery", "Mystery", "Мистика"),
    GenreObj("Romance", "romance", "Romance", "Романтика"),
    GenreObj("Sci-Fi", "sci-fi", "Science Fiction", "Фантастика"),
    GenreObj("Biography", "biography", None, "Биография"),
    GenreObj("History", "history", "History", "Исторический"),
    GenreObj("Adventure", "adventure", "Adventure", "Приключения"),
    GenreObj("Action", "action", "Action", "Экшен"),
    GenreObj("Crime", "crime", "Crime", "Криминал"),
    GenreObj("Drama", "drama", "Drama", "Драма"),
]
