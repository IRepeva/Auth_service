import uuid
from typing import List

from api.v1.models.mixin import MixinModel


class PersonBase(MixinModel):
    full_name: str


class Person(PersonBase):
    role: str | None = ''
    film_ids: List[uuid.UUID | str] | None = []
