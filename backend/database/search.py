import sys
import asyncio
from pathlib import Path
from pydantic import BaseModel
from meilisearch_python_sdk import AsyncClient

sys.path.append(str(Path(__file__).parent.parent.parent))
from backend.settings import settings


MOVIE_INDEX = "movie"
PERSON_INDEX = "person"


class MovieSearchDM(BaseModel):
    id: int
    name_en: str
    name_ru: str | None = None


class PersonSearchDM(BaseModel):
    id: int
    name_en: str


class SearchClient:
    def __init__(self) -> None:
        self._url = f"http://{settings.SEARCH_HOST}:{settings.SEARCH_PORT}"
        self._key = settings.SEARCH_KEY

        self.queue_mode = False
        self.movies_to_add: list[MovieSearchDM] = []
        self.persons_to_add: list[PersonSearchDM] = []

    async def add_movies(self, movies: list[MovieSearchDM]) -> None:
        async with AsyncClient(url=self._url, api_key=self._key) as client:
            await client.index(MOVIE_INDEX).add_documents(
                [m.model_dump() for m in movies]
            )

    async def add_movie(self, movie: MovieSearchDM) -> None:
        if self.queue_mode:
            self.movies_to_add.append(movie)
        else:
            await self.add_movies([movie])

    async def flush_movies_queue(self) -> None:
        if not self.movies_to_add:
            return

        await self.add_movies(self.movies_to_add)
        self.movies_to_add = []

    async def add_persons(self, persons: list[PersonSearchDM]) -> None:
        async with AsyncClient(url=self._url, api_key=self._key) as client:
            await client.index(PERSON_INDEX).add_documents(
                [p.model_dump() for p in persons]
            )

    async def add_person(self, person: PersonSearchDM) -> None:
        if self.queue_mode:
            self.persons_to_add.append(person)
        else:
            await self.add_persons([person])

    async def flush_persons_queue(self) -> None:
        if not self.persons_to_add:
            return

        await self.add_persons(self.persons_to_add)
        self.persons_to_add = []

    async def get_movies(self, query: str) -> list[MovieSearchDM]:
        async with AsyncClient(url=self._url, api_key=self._key) as client:
            data = await client.index(MOVIE_INDEX).search(query)
            return [MovieSearchDM(**m) for m in data.hits]

    async def get_persons(self, query: str) -> list[PersonSearchDM]:
        async with AsyncClient(url=self._url, api_key=self._key) as client:
            data = await client.index(PERSON_INDEX).search(query)
            return [PersonSearchDM(**m) for m in data.hits]

    async def __aenter__(self) -> "SearchClient":
        self.queue_mode = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.flush_movies_queue()
        await self.flush_persons_queue()

        self.queue_mode = False
        return False


async def test():
    client = SearchClient()

    movies = await client.get_movies("щоушенк")
    print(movies)

    persons = await client.get_persons("freeman")
    print(persons)


if __name__ == "__main__":
    asyncio.run(test())
