from django.db import models


class IMDb(models.Model):
    ## max length now is 11
    imdb_mvid = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name="Код IMDb",
    )
    ## max length now is 12
    type = models.CharField(
        max_length=20,
        verbose_name="Тип фильма",
    )

    ## max length RU:208 && EN:106
    title_en = models.CharField(max_length=250, verbose_name="Название англ.")
    title_ru = models.CharField(max_length=250, null=True, verbose_name="Название рус.")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="Slug")

    ### extra-info
    is_adult = models.BooleanField(verbose_name="Для взрослых")
    runtime = models.SmallIntegerField(null=True, verbose_name="Время")

    ### rate-info
    rate = models.FloatField(null=True, verbose_name="Рейтинг IMDb")
    wrate = models.FloatField(null=True, verbose_name="Относительный рейтинг")
    votes = models.IntegerField(null=True, verbose_name="Количество голосов IMDb")

    ### other-resources-info
    ### kinopoisk temporary excluded from project
    ### kp_added = models.BooleanField(blank=True, default=False)
    imdb_extra_added = models.BooleanField(blank=True, default=False)
    tmdb_added = models.BooleanField(blank=True, default=False)

    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на изображение",
    )

    class Meta:
        verbose_name = "Фильм IMDb"
        verbose_name_plural = "Фильмы IMDb"

    def __str__(self) -> str:
        return self.title_en


class Collection(models.Model):
    id = models.IntegerField(primary_key=True)
    name_en = models.CharField(max_length=250)
    name_ru = models.CharField(
        max_length=250,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Коллекция"
        verbose_name_plural = "Коллекции"

    def __str__(self) -> str:
        return self.name_en


class TMDb(models.Model):
    # main-info
    tmdb_mvid = models.IntegerField(primary_key=True)
    imdb_mvid = models.OneToOneField(
        IMDb,
        on_delete=models.CASCADE,
        related_name="tmdb",
    )

    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    # extra-info
    release_date = models.DateField(blank=True, null=True)
    budget = models.BigIntegerField(blank=True, null=True)
    revenue = models.BigIntegerField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    # en-text-info
    tagline_en = models.TextField(blank=True, null=True)
    overview_en = models.TextField(blank=True, null=True)

    # ru-text-info
    tagline_ru = models.TextField(blank=True, null=True)
    overview_ru = models.TextField(blank=True, null=True)

    # rate-info
    rate = models.FloatField(blank=True, null=True)
    votes = models.IntegerField(blank=True, null=True)
    popularity = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "Фильм TMDb"
        verbose_name_plural = "Фильмы TMDb"

    def __str__(self) -> str:
        return str(self.tmdb_mvid)


class KP(models.Model):
    """Temporary excluded"""

    # need to correct max_length
    kp_mvid = models.CharField(
        max_length=20,
        primary_key=True,
    )

    imdb_mvid = models.OneToOneField(IMDb, on_delete=models.CASCADE)

    # text-info
    tagline_ru = models.TextField()
    overview_ru = models.TextField()

    # rate-info
    rate = models.FloatField()
    votes = models.IntegerField()

    # rate-info world film critics
    rate_fc = models.FloatField()
    votes_fc = models.IntegerField()

    # rate-info russian film critics
    rate_rfc = models.FloatField()
    votes_rfc = models.IntegerField()


class Country(models.Model):
    name = models.CharField(
        max_length=200,
        primary_key=True,
    )
    name_ru = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self) -> str:
        return self.name


class MovieCountry(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="movies",
    )
    imdb_mvid = models.ForeignKey(
        IMDb,
        on_delete=models.CASCADE,
        related_name="countries",
    )
    tmdb_mvid = models.ForeignKey(
        TMDb,
        on_delete=models.CASCADE,
        related_name="countries",
    )

    class Meta:
        verbose_name = "Страна фильма"
        verbose_name_plural = "Страны фильма"

    def __str__(self) -> str:
        return f"{self.country}"


class ProductionCompany(models.Model):
    company = models.IntegerField(primary_key=True)

    name = models.CharField(max_length=250)
    country = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    image_url = models.URLField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Продюсерская компания"
        verbose_name_plural = "Продюсерские компании"

    def __str__(self) -> str:
        return self.name


class MovieProduction(models.Model):
    company = models.ForeignKey(ProductionCompany, on_delete=models.CASCADE)
    imdb_mvid = models.ForeignKey(IMDb, on_delete=models.CASCADE)
    tmdb_mvid = models.ForeignKey(TMDb, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Продюсерская компания фильма"
        verbose_name_plural = "Продюсерские компании фильма"


class Genre(models.Model):
    imdb_name = models.CharField(
        max_length=200,
        verbose_name="Название IMDb",
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name="Slug",
        unique=True,
    )

    tmdb_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Название TMDb",
    )
    name_ru = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Название на русском",
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self) -> str:
        return self.imdb_name


class MovieGenre(models.Model):
    imdb_mvid = models.ForeignKey(
        IMDb,
        on_delete=models.CASCADE,
        verbose_name="Название IMDb",
        related_name="genres",
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name="Жанр",
        related_name="movies",
    )

    class Meta:
        verbose_name = "Жанр фильма"
        verbose_name_plural = "Жанры фильма"

    def __str__(self) -> str:
        return f"{self.imdb_mvid.title_en}"
