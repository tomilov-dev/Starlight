import io
import sys
import gzip
from pathlib import Path
from functools import partial
from typing import Generator, Callable, Dict, Iterable

import requests
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(PROJ_DIR))

from services.imdb.notation import AKAS, BASICS, RATINGS, TITLE_REGION as TR

LOCAL_DATA = ROOT_DIR / "imdb" / "local_data"

BASICS_FILTERED = LOCAL_DATA / "title.basics.filtered.csv"
RATINGS_FILTERED = LOCAL_DATA / "title.ratings.filtered.csv"
AKAS_FILTERED = LOCAL_DATA / "title.akas.filtered.csv"

CHUNKSIZE = 100000
TITLE_REGIONS = [TR.RU, TR.US]

ALL_TYPES = [
    "short"
    "movie"
    "tvShort"
    "tvMovie"
    "tvSeries"
    "tvEpisode"
    "tvMiniSeries"
    "tvSpecial"
    "video"
    "videoGame"
    "tvPilot"
]

ALLOWED_TYPES = ["movie"]


class IMDbMovieInterface(object):
    imdb_mvid: str
    type: str
    title_en: str
    title_ru: str
    slug: str
    is_adult: bool
    runtime: int
    rate: float
    wrate: float
    votes: int

    genres: list[str]


class IMDbMovie(IMDbMovieInterface):
    def __init__(self, **kwargs) -> None:
        kwargs = self.check_na(**kwargs)

        self.imdb_mvid = kwargs[BASICS.TCONST]
        self.type = kwargs.get(BASICS.TITLE_TYPE)

        self.title_en = kwargs.get(TR.US, None)
        if self.not_title(self.title_en):
            self.title_en = kwargs.get(BASICS.PRIMARY_TITLE, None)
        if self.not_title(self.title_en):
            self.title_en = kwargs.get(BASICS.ORIGINAL_TITLE, None)
        if self.not_title(self.title_en):
            raise ValueError("No title")

        self.title_ru = kwargs.get(TR.RU, None)
        self.is_adult = kwargs.get(BASICS.IS_ADULT, None)
        self.runtime = kwargs.get(BASICS.RUNTIME, None)

        self.rate = kwargs.get(RATINGS.RATE, None)
        self.wrate = kwargs.get(RATINGS.WRATE, None)
        self.votes = kwargs.get(RATINGS.VOTES)

        self.genres = self.get_genres(kwargs.get(BASICS.GENRES, ""))

        self.init_slug = None

    def set_init_slug(self, slug: str) -> None:
        self.init_slug = slug

    def check_na(self, **kwargs) -> dict:
        for key, value in kwargs.items():
            if pd.isna(value):
                kwargs[key] = None
        return kwargs

    def not_title(self, value) -> bool:
        if value:
            if isinstance(value, str):
                return False
        return True

    def get_genres(self, text: str) -> list[str]:
        genres = []
        if text and isinstance(text, str):
            genres = list(set(map(lambda s: s.strip(), text.split(","))))
        return genres

    @classmethod
    def from_dataframe(cls, dataframe: pd.DataFrame) -> list[IMDbMovieInterface]:
        data: list[IMDbMovieInterface] = []
        for _, series in dataframe.iterrows():
            data.append(cls(**dict(series)))

        return data

    def __repr__(self) -> str:
        return self.title_en


class IMDbPersonInterface(object):
    pass


class IMDbPerson(IMDbPersonInterface):
    pass


def calc_m(
    df: pd.DataFrame,
    percentage: float,
) -> int:
    if percentage < 0 or percentage > 1:
        raise ValueError("Percentage should be in range(0, 1)")

    return np.percentile(
        df[RATINGS.VOTES].values,
        percentage * 100,
    )


def bayesian_rate(
    df: pd.DataFrame,
    m: int | None = None,
) -> pd.Series:
    if m is None:
        m = calc_m(df, 0.995)

    rate = df[RATINGS.RATE]
    votes = df[RATINGS.VOTES]

    avg = rate.mean()  # average rate of average rates

    brate = ((rate * votes) + (avg * m)) / (votes + m)
    return brate


def cast(value, to_type: type):
    try:
        value = to_type(value)
    except:
        value = None
    return value


class CustomFilter:
    def __init__(
        self,
        column: str,
        filter_by: int | str | list,
        reverse: bool = False,
    ) -> None:
        self.column = column
        self.filter_by = filter_by
        self.reverse = reverse

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        iterable = (Iterable, set, list, tuple, pd.Series)

        if self.column in df.columns:
            if self.reverse:
                if isinstance(self.filter_by, iterable):
                    df = df[~df[self.column].isin(self.filter_by)]
                else:
                    df = df[df[self.column] != self.filter_by]

            else:
                if isinstance(self.filter_by, iterable):
                    df = df[df[self.column].isin(self.filter_by)]
                else:
                    df = df[df[self.column] == self.filter_by]

        return df


class IMDbDataSet(object):
    NAME = "name"
    AKAS = "akas"
    BASICS = "basics"
    CREW = "crew"
    EPISODE = "episode"
    PRINCIPALS = "principals"
    RATINGS = "ratings"

    MAPPER = {
        NAME: "https://datasets.imdbws.com/name.basics.tsv.gz",
        AKAS: "https://datasets.imdbws.com/title.akas.tsv.gz",
        BASICS: "https://datasets.imdbws.com/title.basics.tsv.gz",
        CREW: "https://datasets.imdbws.com/title.crew.tsv.gz",
        EPISODE: "https://datasets.imdbws.com/title.episode.tsv.gz",
        PRINCIPALS: "https://datasets.imdbws.com/title.principals.tsv.gz",
        RATINGS: "https://datasets.imdbws.com/title.ratings.tsv.gz",
    }

    def _request_data(
        self,
        data_name: str,
        chunksize: int = CHUNKSIZE,
    ) -> Generator[pd.DataFrame, None, None]:
        if data_name not in self.MAPPER:
            raise ValueError()

        response = requests.get(self.MAPPER[data_name], stream=True)
        if response.status_code == 200:
            with gzip.open(
                io.BytesIO(response.content),
                "rt",
                errors="ignore",
            ) as file:
                yield from pd.read_csv(
                    file,
                    sep="\t",
                    chunksize=chunksize,
                )

    def _get_local_data(
        self,
        path: str,
        chunksize: int = CHUNKSIZE,
    ) -> Generator[pd.DataFrame, None, None] | pd.DataFrame:
        if isinstance(path, Path):
            path = str(path)

        if path.endswith(".csv"):
            data = pd.read_csv(path, chunksize=chunksize)

        elif path.endswith(".tsv"):
            data = pd.read_csv(path, sep="\t", chunksize=chunksize)

        elif path.endswith(".xlsx"):
            data = pd.read_excel(path, chunksize=chunksize)

        else:
            raise ValueError("File should be .csv or .xlsx")

        return data

    def _get_data(
        self,
        data_name: str = None,
        local_path: str = None,
        chunksize: int = 0,
        unpack_chunks: Callable | None = None,
    ) -> pd.DataFrame:
        def default_unpack(
            data_chunks: Generator[pd.DataFrame, None, None],
        ) -> pd.DataFrame:
            data = []
            for chunk in data_chunks:
                data.append(chunk)
            return pd.concat(data)

        if unpack_chunks is None:
            unpack_chunks = default_unpack

        if local_path:
            data_chunks = self._get_local_data(local_path, chunksize)

        else:
            data_chunks = self._request_data(data_name, chunksize)

        return unpack_chunks(data_chunks)

    def get_ratings(
        self,
        local_path: str | None = None,
        chunksize: int = CHUNKSIZE,
    ) -> pd.DataFrame:
        return self._get_data(
            self.RATINGS,
            local_path,
            chunksize,
        )

    def get_basics(
        self,
        local_path: str | None = None,
        chunksize: int = CHUNKSIZE,
        min_year: int | None = 1990,
        max_year: int | None = 2040,
        allowed_types: list[str] = ALLOWED_TYPES,
    ) -> pd.DataFrame:
        def unpack_chunks(
            data_chunks: Generator[pd.DataFrame, None, None]
        ) -> pd.DataFrame:
            to_int = partial(cast, to_type=int)

            data: list[pd.DataFrame] = []
            for chunk in data_chunks:
                chunk[BASICS.START_YEAR] = chunk[BASICS.START_YEAR].apply(to_int)

                if min_year is not None:
                    chunk = chunk[chunk[BASICS.START_YEAR] >= min_year]

                if max_year is not None:
                    chunk = chunk[chunk[BASICS.START_YEAR] <= max_year]

                if allowed_types is not None:
                    chunk = chunk[chunk[BASICS.TITLE_TYPE].isin(allowed_types)]

                data.append(chunk)

            return pd.concat(data)

        return self._get_data(
            self.BASICS,
            local_path,
            chunksize,
            unpack_chunks=unpack_chunks,
        )

    def get_akas(
        self,
        local_path: str | None = None,
        chunksize: int = CHUNKSIZE,
        title_regions: list[str] = TITLE_REGIONS,
        customf: CustomFilter | None = None,
    ) -> Dict[TR, pd.DataFrame]:
        def unpack_chunks(
            data_chunks: Generator[pd.DataFrame, None, None]
        ) -> Dict[TR, pd.DataFrame]:
            def sort_key(value):
                if value == "imdbDisplay":
                    return 0
                else:
                    return 1

            data_by_region: Dict[TR, list[pd.DataFrame]] = {
                tr: [] for tr in title_regions
            }

            for chunk in data_chunks:
                for title_region in title_regions:
                    rchunk = chunk[chunk[AKAS.REGION] == title_region]
                    if customf:
                        rchunk = customf.filter(rchunk)

                    data_by_region[title_region].append(rchunk)

            for title_region in data_by_region:
                data_by_region[title_region] = (
                    pd.concat(data_by_region[title_region])
                    .sort_values(by=[AKAS.TYPES], key=lambda x: x.map(sort_key))
                    .drop_duplicates(subset=[AKAS.TCONST])
                    .rename(columns={AKAS.TITLE: title_region})
                )[[AKAS.TCONST, title_region, AKAS.TYPES]]

            return data_by_region

        return self._get_data(
            self.AKAS,
            local_path,
            chunksize=chunksize,
            unpack_chunks=unpack_chunks,
        )

    def check_nulls(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.replace(r"\N", None)

    def get_movies(
        self,
        amount: int = 10000,
        debug: bool = False,
    ) -> list[IMDbMovie]:
        # if debug - we use local filtered (small) dumps
        if debug:
            data = self.get_basics(BASICS_FILTERED)
            ratings = self.get_ratings(RATINGS_FILTERED)
            akas = self.get_akas(AKAS_FILTERED, title_regions=TITLE_REGIONS)

        else:
            data = self.get_basics()
            ratings = self.get_ratings()
            akas = self.get_akas(title_regions=TITLE_REGIONS)

        ### should we filter it before make wrate?
        ratings[RATINGS.WRATE] = bayesian_rate(ratings)

        data = data.merge(
            ratings,
            how="left",
            left_on=BASICS.TCONST,
            right_on=BASICS.TCONST,
        )

        for title_region in akas:
            data = data.merge(
                akas[title_region][[AKAS.TCONST, title_region]],
                how="left",
                left_on=BASICS.TCONST,
                right_on=AKAS.TCONST,
            )

        data = self.check_nulls(data)

        # filter films without any rate
        data = data[data[RATINGS.RATE].notna()]

        data = data.sort_values(by=[RATINGS.WRATE], ascending=False)

        # preprocess
        to_int = partial(cast, to_type=int)
        to_float = partial(cast, to_type=float)
        to_bool = partial(cast, to_type=bool)

        data[BASICS.IS_ADULT] = data[BASICS.IS_ADULT].apply(to_bool)
        data[BASICS.RUNTIME] = data[BASICS.RUNTIME].apply(to_int)
        data[RATINGS.RATE] = data[RATINGS.RATE].apply(to_float)
        data[RATINGS.WRATE] = data[RATINGS.WRATE].apply(to_float)
        data[RATINGS.VOTES] = data[RATINGS.VOTES].apply(to_int)

        # temporary backup
        # data[:amount].to_excel("check.xlsx", index=False)

        return IMDbMovie.from_dataframe(
            data[:amount],
        )

    def get_crew(
        self,
        local_path: str | None = None,
        chunksize: int = CHUNKSIZE,
        mvids: list[str] = [],
    ):
        def unpack_chunks(
            data_chunks: Generator[pd.DataFrame, None, None]
        ) -> pd.DataFrame:
            data: list[pd.DataFrame] = []
            for data_chunk in data_chunks:
                data.append(data_chunk)

            return pd.concat(data)

        return self._get_data(
            self.RATINGS,
            local_path,
            chunksize,
            unpack_chunks=unpack_chunks,
        )

    def get_actors(self, mvids: list[str] = []) -> list[IMDbPerson]:
        crew = self.get_crew(
            "/home/mainus/Projects/Starlight/starlight_backend/data/title.crew.tsv",
            mvids=mvids,
        )

        print(crew)


if __name__ == "__main__":
    ds = IMDbDataSet()
    ds.get_actors()
