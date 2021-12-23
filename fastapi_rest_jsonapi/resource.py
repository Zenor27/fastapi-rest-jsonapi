from fastapi_rest_jsonapi.methods import Methods
from typing import Optional
from fastapi_rest_jsonapi.schema import Schema


class Resource:
    methods = Methods.values()
    schema: Schema = None
    data_layer = None

    @staticmethod
    def get(cls, q: Optional[str] = None):
        raise NotImplementedError

    @staticmethod
    def post(cls, q: Optional[str] = None):
        raise NotImplementedError

    @staticmethod
    def put(cls, q: Optional[str] = None):
        raise NotImplementedError

    @staticmethod
    def delete(cls, q: Optional[str] = None):
        raise NotImplementedError

    @staticmethod
    def patch(cls, q: Optional[str] = None):
        raise NotImplementedError
