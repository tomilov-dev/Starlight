import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))
from movie_genres import genres


@pytest.mark.asyncio
async def test_movie_genres():
    genre = [g for g in genres if g.name_en == "Drama"][0]

    genre.slug = "drama"
    genre.name_ru = "Драма"
    genre.tmdb_name = "Drama"
