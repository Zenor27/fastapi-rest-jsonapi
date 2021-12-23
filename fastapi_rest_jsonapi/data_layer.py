from abc import ABCMeta, abstractmethod


class DataLayer(metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_one(self, id: int) -> object:
        raise NotImplementedError
