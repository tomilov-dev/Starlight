"""Transform full dataset to working dataset with size 1000"""

import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from dataset import (
    bayesian_rate,
    IMDbDataSet,
    CustomFilter,
    RATINGS,
    BASICS,
    AKAS,
    CHUNKSIZE,
    TITLE_REGIONS,
)

LOCAL_DATA = ROOT_DIR / "local_data"
AKAS_PATH = "title.akas.tsv"
BASICS_PATH = "title.basics.tsv"
RATINGS_PATH = "title.ratings.tsv"

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

    ratings.to_csv(LOCAL_DATA / "title.ratings.filtered.csv")
    basics.to_csv(LOCAL_DATA / "title.basics.filtered.csv")
    akas.to_csv(LOCAL_DATA / "title.akas.filtered.csv")


if __name__ == "__main__":
    filter_movies()
