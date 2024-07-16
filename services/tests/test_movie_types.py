import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))
from services.content_types import content_types


@pytest.mark.asyncio
async def test_movie_types():
    mtype = [t for t in content_types if t.imdb_name == "movie"][0]

    mtype.name_en = "Movie"
    mtype.name_ru = "Фильм"
