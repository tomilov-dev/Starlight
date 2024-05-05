import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent


class CountryObj:
    """Simple wrapper for movie countries"""

    def __init__(
        self,
        iso: str,
        name_en: str,
        name_ru: str,
    ) -> None:
        self.iso = iso
        self.name_en = name_en
        self.name_ru = name_ru

    def __repr__(self) -> str:
        return f"{self.name_en} : {self.name_ru}"


def read_json() -> list[CountryObj]:
    """Read countries.json file and extract prepared countries from IMDb"""

    countries: list[CountryObj] = []
    with open(ROOT_DIR / "countries.json", "r", encoding="utf-8") as file:
        data: list[dict] = json.loads(file.read())

        for country in data:
            ru = country["russian_name"]
            if not ru or ru is None:
                print(country)

            countries.append(
                CountryObj(
                    iso=country.get("iso_3166_1"),
                    name_en=country.get("english_name", None),
                    name_ru=country.get("russian_name", None),
                ),
            )

    return countries


countries = read_json()
