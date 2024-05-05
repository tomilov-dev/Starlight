"""Content types according IMDb"""


class TypeObj:
    """Simple wrapper for movie types"""

    def __init__(
        self,
        imdb: str,
        name_en: str,
        name_ru: str,
    ) -> None:
        self.imdb = imdb
        self.name_en = name_en
        self.name_ru = name_ru

    def __repr__(self) -> str:
        return f"{self.name_en}, {self.name_ru}"


types: list[TypeObj] = [
    TypeObj("movie", "Movie", "Фильм"),
    TypeObj("short", "Short Movie", "Короткометражка"),
    TypeObj("tvEpisode", "TV Episode", "Телевизионный эпизод"),
    TypeObj("tvMiniSeries", "TV Mini Series", "Телевизионный мини-сериал"),
    TypeObj("tvMovie", "TV Movie", "Телевизионный фильм"),
    TypeObj("tvSeries", "TV Series", "Телевизионный сериал"),
    TypeObj("tvShort", "TV Short", "Телевизионная короткометражка"),
    TypeObj("tvSpecial", "TV Special", "Телевизионный спецвыпуск"),
    TypeObj("video", "Video", "Видео"),
    TypeObj("videoGame", "Video Game", "Видео-игра"),
]

imdbTypesMapper = {t.imdb: t for t in types}
