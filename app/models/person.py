import uuid
from typing import List

from api.v1.models import MixinModel


class Person(MixinModel):
    full_name: str
    role: str | None = ''
    film_ids: List[uuid.UUID | str] | None = []
