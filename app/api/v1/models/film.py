from typing import List

from api.v1.models.genre import Genre
from api.v1.models.mixin import MixinModel
from api.v1.models.person import PersonBase


class Film(MixinModel):
    title: str
    imdb_rating: float | None = 0


class FilmDetails(Film):
    description: str | None = ''
    genres: List[Genre] | None = []
    directors: List[PersonBase] | None = []
    writers: List[PersonBase] | None = []
    actors: List[PersonBase] | None = []
