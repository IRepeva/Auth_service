import sys
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

sys.path.append('.')
from api.v1.models.film import FilmDetails, Film
from api.v1.utils.errors import NotFoundDetail
from services.films import FilmService, get_film_service
from utils.cache import Cache

router = APIRouter()


@router.get('/search', response_model=List[Film], summary='Get search results')
@Cache()
async def films_search(
        sort: str | None = None,
        query: str | None = None,
        page: int | None = Query(default=1, alias='page[number]'),
        page_size: int | None = Query(default=50, alias='page[size]'),
        film_service: FilmService = Depends(get_film_service)
) -> List[Film]:
    """
    Search for a movie matching the query parameter 'query'.

    Pagination settings can be passed using 'page[size]' and 'page[number]'
    parameters, default settings are: page size=50, page number=1

    If 'query' is omitted than all movies with pagination settings will be retrieved

    Movie information:
    - **id**: each film has a unique id
    - **title**: film title
    - **imdb_rating**: rating of the movie
    """
    films_list = await film_service.get_list(query=query, sort=sort,
                                             page=page, page_size=page_size)
    if not films_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.FILMS
        )

    return films_list


@router.get('/{film_id}', response_model=FilmDetails, summary="Get film by id")
@Cache()
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> FilmDetails:
    """
    Get all film information:

    - **id**: each film has a unique id
    - **title**: film title
    - **description**: short film description
    - **imdb_rating**: rating of the movie
    - **genres**: list of film genres
    - **directors**: list of film directors
    - **writers**: list of film writers
    - **actors**: list of film actors
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.FILM
        )

    return film


@router.get('/', response_model=List[Film], summary='Get all movies')
@Cache()
async def films(
        sort: str | None = None,
        similar_to: str | None = None,
        genre: str | None = Query(default=None, alias='filter[genre]'),
        page: int | None = Query(default=1, alias='page[number]'),
        page_size: int | None = Query(default=50, alias='page[size]'),
        film_service: FilmService = Depends(get_film_service)
) -> List[Film]:
    """
    Get all movies with pagination settings.

    Pagination settings can be passed using 'page[size]' and 'page[number]'
    parameters, default settings are: page size=50, page number=1

    Movie information:
    - **id**: each film has a unique id
    - **title**: film title
    - **imdb_rating**: rating of the movie
    """
    films_list = await film_service.get_list(sort=sort, genre=genre,
                                             similar_to=similar_to,
                                             page=page, page_size=page_size)
    if not films_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.FILMS
        )
    return films_list
