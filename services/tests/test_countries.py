import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))
from countries import countries


@pytest.mark.asyncio
async def test_countries():
    country = [c for c in countries if c.iso == "RU"][0]
    country.name_en = "Russia"
    country.name_ru = "Россия"
