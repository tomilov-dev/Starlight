import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from services.models import CountrySDM


def read_json() -> list[CountrySDM]:
    """Read countries.json file and extract prepared countries from IMDb"""

    countries: list[CountrySDM] = []
    with open(ROOT_DIR / "services" / "countries.json", "r", encoding="utf-8") as file:
        data: list[dict] = json.loads(file.read())

        for country in data:
            ru = country["russian_name"]
            if not ru or ru is None:
                print(country)

            countries.append(
                CountrySDM(
                    iso=country.get("iso_3166_1"),
                    name_en=country.get("english_name"),
                    name_ru=country.get("russian_name", None),
                )
            )

    return countries


countries = read_json()
