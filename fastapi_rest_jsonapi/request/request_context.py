import re
from pydantic import BaseModel
from typing import Optional
from starlette.datastructures import URL
from fastapi_rest_jsonapi.request.field import Field
from fastapi_rest_jsonapi.request.page import Page
from fastapi_rest_jsonapi.request.sort import Sort


class RequestContext:
    def __init__(
        self,
        url: URL,
        path_parameters: Optional[BaseModel] = None,
        query_parameters: Optional[dict] = None,
        body: Optional[dict] = None,
    ) -> None:
        self.url = url
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.body = body

        self._sorts = None
        self._fields = None
        self._page = None

    @property
    def sorts(self) -> list[Sort]:
        if self._sorts:
            return self._sorts

        sorts = []
        query_sort = self.query_parameters.get("sort")
        if query_sort is None:
            return sorts

        for sort in query_sort.split(","):
            if sort.startswith("-"):
                sorts.append(Sort(field=sort[1:], ascending=False))
            else:
                sorts.append(Sort(field=sort, ascending=True))

        self._sorts = sorts
        return sorts

    @property
    def fields(self) -> list[Field]:
        if self._fields:
            return self._fields

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

        self._fields = fields
        return fields

    @property
    def page(self) -> Page:
        if self._page:
            return self._page

        regex = r"\[(?P<param_type>.*)\]=(?P<param_value>.*)"
        query_page = self.query_parameters.get("page")
        if query_page is None:
            return None

        page_size = None
        page_number = None

        for page_ in query_page:
            if m := re.search(regex, page_):
                param_type = m.group("param_type")
                param_value = m.group("param_value")
                if param_type == "number":
                    page_number = int(param_value)
                elif param_type == "size":
                    page_size = int(param_value)

        if page_number is None:
            page_number = 1

        page = Page(self.url, self.query_parameters, page_number, page_size)
        self._page = page
        return page
