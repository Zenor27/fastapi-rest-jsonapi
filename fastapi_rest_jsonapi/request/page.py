from urllib.parse import unquote
from typing import Optional
from starlette.datastructures import URL


PAGE_NUMBER_QUERY_PARAM = "page[number]"


class Page:
    def __init__(self, url: URL, number: int, size: Optional[int] = None) -> None:
        self.url = url
        self.number = number
        self.size = size
        self.max_number = None

    def is_paginated(self):
        return self.size is not None and self.size > 0

    def __get_query_params_as_dict(self) -> dict:
        query_params = unquote(self.url.query).split("&")
        if not len(query_params) or query_params[0] == "":
            return {}
        return {k: v for k, v in [param.split("=") for param in query_params]}

    def get_self_link(self) -> str:
        return str(self.url)

    def get_first_link(self) -> str:
        query_params_as_dict = self.__get_query_params_as_dict()
        query_params_as_dict[PAGE_NUMBER_QUERY_PARAM] = 1
        return str(self.url.replace_query_params(**query_params_as_dict))

    def get_prev_link(self) -> str:
        if self.number <= 1:
            return None
        query_params_as_dict = self.__get_query_params_as_dict()
        query_params_as_dict[PAGE_NUMBER_QUERY_PARAM] = self.number - 1
        return str(self.url.replace_query_params(**query_params_as_dict))

    def get_next_link(self) -> str:
        if self.number >= self.max_number:
            return None

        query_params_as_dict = self.__get_query_params_as_dict()
        query_params_as_dict[PAGE_NUMBER_QUERY_PARAM] = self.number + 1
        return str(self.url.replace_query_params(**query_params_as_dict))

    def get_last_link(self) -> str:
        query_params_as_dict = self.__get_query_params_as_dict()
        query_params_as_dict[PAGE_NUMBER_QUERY_PARAM] = self.max_number
        return str(self.url.replace_query_params(**query_params_as_dict))
