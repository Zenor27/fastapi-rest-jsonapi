from abc import ABCMeta, abstractmethod
from fastapi_rest_jsonapi.request.include import Include
from fastapi_rest_jsonapi.request.page import Page
from fastapi_rest_jsonapi.request.sort import Sort
from fastapi_rest_jsonapi.request.field import Field


class DataLayer(metaclass=ABCMeta):
    @abstractmethod
    def get(
        self, sorts: list[Sort] = None, fields: list[Field] = None, page: Page = None, includes: list[Include] = None
    ) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_one(self, id_: int, fields: list[Field] = None, includes: list[Include] = None) -> object:
        raise NotImplementedError

    @abstractmethod
    def delete_one(self, id_: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update_one(self, id_: int, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    def create_one(self, **kwargs) -> object:
        raise NotImplementedError
