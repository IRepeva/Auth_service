from typing import List

from api.v1.models import Genre
from api.v1.models import MixinModel
from api.v1.models import Person


class Film(MixinModel):
    title: str
    description: str | None = ''
    imdb_rating: float | None = 0
    genres: List[Genre] | None = []
    directors: List[Person] | None = []
    writers: List[Person] | None = []
    actors: List[Person] | None = []
