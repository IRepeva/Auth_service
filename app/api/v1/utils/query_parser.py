from services.base import BaseService


class QueryParser:
    @staticmethod
    async def parse_params(service: BaseService, **kwargs):
        for param, value in kwargs.items():
            if value:
                return {'query': await service.get_query(param, value)}
        return {}

    @staticmethod
    def parse_sort(sort: str | None = None):
        return (
            sort.removeprefix('-') + ':desc' if sort.startswith('-') else
            sort + ':asc'
        )
