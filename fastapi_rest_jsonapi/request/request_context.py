import re
from pydantic import BaseModel
from typing import Optional
from starlette.datastructures import URL
from fastapi_rest_jsonapi.common import memoized_property
from fastapi_rest_jsonapi.request.field import Field
from fastapi_rest_jsonapi.request.include import Include
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

    @memoized_property
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

    @memoized_property
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

    @memoized_property
    def page(self) -> Optional[Page]:
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
        return page

    @memoized_property
    def includes(self) -> list[Include]:
        includes = []
        query_include = self.query_parameters.get("include")
        if query_include is None:
            return includes

        for include in query_include.split(","):
            includes.append(Include(field=include))

        return includes
