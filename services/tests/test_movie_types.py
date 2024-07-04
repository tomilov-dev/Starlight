import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))
from movie_types import movie_types


@pytest.mark.asyncio
async def test_movie_types():
    mtype = [t for t in movie_types if t.imdb_name == "movie"][0]

    mtype.name_en = "Movie"
    mtype.name_ru = "Фильм"
