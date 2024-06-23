"""Transform full dataset to working dataset with size 1000"""

import sys
import asyncio
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from dataset import (
    bayesian_rate,
    IMDbDataSet,
    CustomFilter,
    PRINCIPALS,
    RATINGS,
    BASICS,
    AKAS,
    LOCAL_DATA,
    AKAS_FILTERED,
    BASICS_FILTERED,
    PERSONS_FILTERED,
    RATINGS_FILTERED,
    PRINCIPALS_FILTERED,
)

AKAS_PATH = "title.akas.tsv"
BASICS_PATH = "title.basics.tsv"
RATINGS_PATH = "title.ratings.tsv"

PRINCIPALS_PATH = "title.principals.tsv"
NAME_PATH = "name.basics.tsv"

DEBUG_SIZE = 1000


def filter_movies():
    dataset = IMDbDataSet()

    # upload
    ratings = dataset.get_ratings(str(LOCAL_DATA / RATINGS_PATH))

    selector = ratings.copy()
    selector[RATINGS.WRATE] = bayesian_rate(selector)
    selector = selector[selector[RATINGS.RATE].notna()]

    # upload basics
    basics = dataset.get_basics(
        str(LOCAL_DATA / BASICS_PATH),
        allowed_types=["movie"],
    )

    selector = pd.merge(
        basics,
        selector,
        how="left",
        left_on=BASICS.TCONST,
        right_on=RATINGS.TCONST,
    )

    selector = selector.sort_values(by=[RATINGS.WRATE], ascending=False)
    selector = selector[:DEBUG_SIZE]

    ids = selector[RATINGS.TCONST]

    ratingsf = CustomFilter(RATINGS.TCONST, ids)
    basicsf = CustomFilter(BASICS.TCONST, ids)
    akasf = CustomFilter(AKAS.TCONST, ids)

    # upload akas
    akas_dict = dataset.get_akas(str(LOCAL_DATA / AKAS_PATH), customf=akasf)

    akas_list = []
    for title_region, df in akas_dict.items():
        df[AKAS.REGION] = title_region
        df = df.rename(columns={title_region: AKAS.TITLE})
        akas_list.append(df)

    akas = pd.concat(akas_list)

    ratings = ratingsf.filter(ratings)
    basics = basicsf.filter(basics)

    ratings.to_csv(RATINGS_FILTERED)
    basics.to_csv(BASICS_FILTERED)
    akas.to_csv(AKAS_FILTERED)


def filter_persons():
    ds = IMDbDataSet()

    movies = ds.get_movies(debug=True)
    imdb_mvids = [m.imdb_mvid for m in movies]

    principals = ds.get_principals(
        LOCAL_DATA / PRINCIPALS_PATH,
        imdb_mvids=imdb_mvids,
    )
    imdb_nmids = list(set(principals[PRINCIPALS.NCONST]))

    persons = ds.get_names(
        LOCAL_DATA / NAME_PATH,
        imdb_nmids=imdb_nmids,
    )

    principals.to_csv(PRINCIPALS_FILTERED)
    persons.to_csv(PERSONS_FILTERED)


if __name__ == "__main__":
    # filter_movies()
    filter_persons()
