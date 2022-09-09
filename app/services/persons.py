from functools import lru_cache
from typing import List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl import Q
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from api.v1.models import Person
from services.base import BaseService


class PersonService(BaseService):
    INDEX = 'persons'
    MODEL = Person

    @property
    def query(self):
        return lambda query: Q('match', full_name={'query': query})

    async def add_person_movies(
            self, persons: Person | List[Person]
    ) -> List[Person] | None:

        from services.films import FilmService
        film_service = FilmService(self.redis, self.elastic)

        if isinstance(persons, Person):
            persons = [persons]

        persons_data = {person.id: person.full_name for person in persons}

        try:
            films = await film_service.get_list(person=list(persons_data))
        except NotFoundError:
            return None

        if not films:
            return persons

        persons_films = []
        for p_id, p_name in persons_data.items():
            self._set_films_to_person(persons_films, p_id, p_name, films)

        if not persons_films:
            return persons

        return persons_films

    def _set_films_to_person(
            self,
            persons_films: list,
            person_id: str,
            person_name: str,
            films: dict
    ) -> None:
        """
        Parse films ids by roles for person id and add them to general list
        of persons films
        """

        roles = {
            ('directors', 'director'): [],
            ('writers', 'writer'): [],
            ('actors', 'actor'): []
        }

        def check_func(item):
            return item.id == person_id

        for film in films:
            for role in roles:
                if list(filter(check_func, getattr(film, role[0]))):
                    roles[role].append(film.id)

        for role in roles:
            if roles[role]:
                persons_films.append(
                    Person(id=person_id, full_name=person_name,
                           role=role[1], film_ids=roles[role])
                )


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(redis, elastic)
