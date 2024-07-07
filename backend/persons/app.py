import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException


sys.path.append(Path(__file__).parent.parent)

from persons.manager.imdb_persons import IMDbPersonManager
from persons.models import (
    IMDbPersonDTOBase,
    IMDbPersonDTOExtended,
    ProfessionDTO,
    IMDbMovieBaseDTO,
)

imdbPM = IMDbPersonManager()

router = APIRouter()


@router.get("/search/persons/{query}")
async def search_persons(query: str) -> list[IMDbPersonDTOBase]:
    persons = await imdbPM.search_persons(query)
    return [IMDbPersonDTOBase.model_validate(p, from_attributes=True) for p in persons]


@router.get("/persons")
async def get_persons():
    persons = await imdbPM.get_persons()
    persons = [
        IMDbPersonDTOBase.model_validate(p, from_attributes=True) for p in persons
    ]
    return persons


@router.get("/persons/{slug}")
async def get_person(slug: str):
    person = await imdbPM.get_person(slug)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    return IMDbPersonDTOExtended.model_validate(person, from_attributes=True)
