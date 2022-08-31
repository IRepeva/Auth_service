from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.v1.models.genre import Genre
from api.v1.utils.errors import NotFoundDetail
from services.genres import GenreService, get_genre_service
from utils.cache import Cache

router = APIRouter()


@router.get('/', response_model=List[Genre], summary='Get all genres')
@Cache()
async def genres_list(
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    """
    Get list of all genres with the information:

    - **id**: each genre has a unique id
    - **name**: genre name
    """
    genres = await genre_service.get_list()
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.GENRES
        )

    return genres


@router.get('/{genre_id}', response_model=Genre, summary="Get genre by id")
@Cache()
async def genre_by_id(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    """
    Get all genre information:

    - **id**: each genre has a unique id
    - **name**: genre name
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=NotFoundDetail.GENRE
        )

    return genre
