import re
from pydantic import BaseModel
from typing import Optional
from fastapi_rest_jsonapi.request.field import Field
from fastapi_rest_jsonapi.request.sort import Sort


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

    @property
    def fields(self) -> list[Field]:
        regex = r"\[(?P<type>.*)\]=(?P<fields>.*)"
        fields = []
        query_field = self.query_parameters.get("field")
        if query_field is None:
            return fields

        for field in query_field:
            if m := re.search(regex, field):
                type = m.group("type")
                type_fields = m.group("fields").split(",")
                fields.extend([Field(type, type_field) for type_field in type_fields])

        return fields
