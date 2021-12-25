from pydantic import BaseModel
from typing import Optional

from fastapi_rest_jsonapi.sort import Sort


class RequestContext:
    def __init__(
        self,
        path_parameters: Optional[BaseModel] = None,
        query_parameters: Optional[dict] = None,
        body: Optional[dict] = None,
    ) -> None:
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.body = body

    @property
    def sorts(self) -> list[Sort]:
        sorts = []
        query_sort = self.query_parameters.get("sort")
        if query_sort is None:
            return sorts

        for sort in query_sort.split(","):
            if sort.startswith("-"):
                sorts.append(Sort(field=sort[1:], ascending=False))
            else:
                sorts.append(Sort(field=sort, ascending=True))
        return sorts
