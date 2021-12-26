from abc import ABCMeta, abstractmethod

from fastapi_rest_jsonapi.sort import Sort


class DataLayer(metaclass=ABCMeta):
    @abstractmethod
    def get(self, sorts: list[Sort]) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_one(self, id: int) -> object:
        raise NotImplementedError

    @abstractmethod
    def delete_one(self, id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update_one(self, id: int, **kwargs) -> object:
        raise NotImplementedError

    @abstractmethod
    def create_one(self, **kwargs) -> object:
        raise NotImplementedError
