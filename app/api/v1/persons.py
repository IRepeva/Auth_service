from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.models.film import Film
from api.v1.models.person import Person
from api.v1.utils.errors import NotFoundDetail
from services.films import FilmService, get_film_service
from services.persons import PersonService, get_person_service
from utils.cache import Cache

router = APIRouter()


@router.get('/search', response_model=List[Person],
            summary='Get search results')
@Cache()
async def persons_search(
        query: str | None = None,
        page: int | None = Query(default=1, alias='page[number]'),
        page_size: int | None = Query(default=50, alias='page[size]'),
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    """
    Search for a person matching the query parameter 'query'.

    Pagination settings can be passed using 'page[size]' and 'page[number]' parameters,
    default settings are: page size=50, page number=1

    If 'query' is omitted than all persons with pagination settings will be retrieved

    Person information:
    - **id**: each person has a unique id
    - **full_name**: person's full_name
    - **role**: person's role
    - **film_ids**: list of films in which a person participated in a particular role
    """
    persons = await person_service.get_list(query=query, page=page,
                                            page_size=page_size)
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.PERSONS
        )

    persons_list = await person_service.add_person_movies(persons)
    return persons_list


@router.get('/{person_id}/film', response_model=List[Film],
            summary="Get all person's films")
@Cache()
async def person_films(
        person_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> List[Film]:
    """
    Get all films of the specific person with the information:

    - **id**: each film has a unique id
    - **title**: film title
    - **imdb_rating**: rating of the movie
    """
    films = await film_service.get_list(person=person_id)

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.FILMS
        )

    return films


@router.get('/{person_id}', response_model=List[Person],
            summary="Get person by id")
@Cache()
async def person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    """
    Get list of all persons with pagination settings.

    Pagination settings can be passed using 'page[size]' and 'page[number]' parameters,
    default settings are: page size=50, page number=1

    Person information:
    - **id**: each person has a unique id
    - **full_name**: person's full_name
    - **role**: person's role
    - **film_ids**: list of films in which a person participated in a particular role
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.PERSON
        )

    return await person_service.add_person_movies(person)
