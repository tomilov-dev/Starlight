import re
import sys
from pathlib import Path

import pytest

PROJ_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJ_DIR))

from services.imdb.dataset import IMDbDataSet


class TestIMDbDataset:
    def get_dataset(self) -> IMDbDataSet:
        return IMDbDataSet(debug=True)

    def test_dataset_movie(self):
        ds = self.get_dataset()

        movies = ds.get_movies()

        # search Shawshank Redemption tt0111161
        movie = [m for m in movies if m.imdb_mvid == "tt0111161"][0]

        assert movie.name_en == "The Shawshank Redemption"
        assert movie.name_ru == "Побег из Шоушенка"
        assert movie.init_slug == None
        assert movie.type == "movie"
        assert movie.is_adult == False
        assert movie.runtime == 142
        assert movie.rate >= 9
        assert movie.wrate >= 8
        assert movie.votes >= 2500000
        assert "Drama" in movie.genres

    def test_dataset_movie_crew(self):
        ds = self.get_dataset()

        principals, persons = ds.get_movie_crew(["tt0111161"])

        principal = [pr for pr in principals if pr.imdb_person == "nm0000151"][0]
        assert principal.imdb_movie == "tt0111161"
        assert principal.ordering == 2
        assert principal.category == "actor"
        assert principal.job == None
        assert any(re.search("red", c, re.IGNORECASE) for c in principal.characters)

        person = [p for p in persons if p.imdb_nmid == principal.imdb_person][0]
        assert person.name_en == "Morgan Freeman"
        assert person.name_ru == None
        assert person.init_slug == None
        assert person.birth_y == 1937
        assert person.professions == None
        assert "tt0097239" in person.known_for_titles
