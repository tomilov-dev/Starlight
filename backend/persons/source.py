import sys
import asyncio
from datetime import datetime
from pathlib import Path

PROJ_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(PROJ_DIR))

from backend.database.manager import SourceDataModel, AbstractPersonDataSource
from services.person_professions import professions
from services.imdb.dataset import IMDbDataSet
from services.models import IMDbPrincipalServiceDM, IMDbPersonServiceDM


class ProfessionSourceDM(SourceDataModel):
    name_en: str
    name_ru: str | None = None
    imdb_name: str

    crew: bool

    @property
    def to_exclude(self) -> list[str]:
        return ["crew"]


class IMDbPersonSourceDM(SourceDataModel):
    imdb_nmid: str
    name_en: str

    birth_y: int | None = None
    death_y: int | None = None
    professions: list[ProfessionSourceDM] = []

    slug: str | None = None
    image_url: str | None = None

    @property
    def to_exclude(self) -> list[str]:
        return ["professions", "slug"]


class IMDbPrincipalSourceDM(SourceDataModel):
    imdb_movie: str
    imdb_person: str
    category: ProfessionSourceDM | None = None  # profession

    ordering: int
    job: str | None = None
    characters: list[str] = []

    @property
    def to_exclude(self) -> list[str]:
        return ["imdb_movie", "imdb_person", "category"]


class PersonDataSource(AbstractPersonDataSource):
    __instance = None

    def __new__(cls) -> "PersonDataSource":
        if cls.__instance is None:
            cls.__instance = super(PersonDataSource, cls).__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        self.imdb_ds = IMDbDataSet(debug=True)

        self.professions = {p.imdb_name: p for p in self.get_professions()}

    def get_professions(self) -> list[ProfessionSourceDM]:
        return [
            ProfessionSourceDM(
                name_en=p.name_en,
                name_ru=p.name_ru,
                imdb_name=p.imdb_name,
                crew=p.crew,
            )
            for p in professions
        ]

    def prepare_person(
        self,
        person: IMDbPersonServiceDM,
    ) -> IMDbPersonSourceDM:
        professions = []
        if person.professions:
            professions = [self.professions.get(p) for p in person.professions]
            professions = [p for p in professions if p is not None]

        return IMDbPersonSourceDM(
            imdb_nmid=person.imdb_nmid,
            name_en=person.name_en,
            birth_y=person.birth_y,
            death_y=person.death_y,
            professions=professions,
        )

    def prepare_principal(
        self,
        principal: IMDbPrincipalServiceDM,
    ) -> IMDbPrincipalSourceDM:
        characters = principal.characters if principal.characters else []
        category = self.professions.get(principal.category, None)
        return IMDbPrincipalSourceDM(
            imdb_movie=principal.imdb_movie,
            imdb_person=principal.imdb_person,
            category=category,
            ordering=principal.ordering,
            job=principal.job,
            characters=characters,
        )

    async def get_movie_crew(
        self,
        imdb_mvids: list[str],
    ) -> tuple[list[IMDbPrincipalSourceDM], list[IMDbPersonSourceDM]]:
        principals, persons = self.imdb_ds.get_movie_crew(imdb_mvids)
        return [self.prepare_principal(p) for p in principals], [
            self.prepare_person(p) for p in persons
        ]

    async def get_imdb_principals(
        self,
        imdb_mvids: list[str],
    ) -> list[IMDbPrincipalSourceDM]:
        principals, _ = self.imdb_ds.get_movie_crew(imdb_mvids)
        return [self.prepare_principal(p) for p in principals]

    async def get_imdb_persons(
        self,
        imdb_mvids: list[str],
    ) -> list[IMDbPersonSourceDM]:
        _, persons = self.imdb_ds.get_movie_crew(imdb_mvids)
        return [self.prepare_person(p) for p in persons]


async def test():
    ds = PersonDataSource()

    # professions = ds.get_professions()


if __name__ == "__main__":
    asyncio.run(test())
