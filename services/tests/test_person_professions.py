import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))

from person_professions import professions


@pytest.mark.asyncio
async def test_professions():
    profession = [t for t in professions if t.imdb_name == "editor"][0]

    profession.name_en = "Editor"
    profession.name_ru = "Монтажер"
    profession.crew = False
