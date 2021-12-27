from __future__ import annotations
from abc import ABCMeta, abstractstaticmethod

from fastapi_rest_jsonapi.data import DataLayer
from fastapi_rest_jsonapi.common import Methods
from fastapi_rest_jsonapi.schema import Schema
from fastapi_rest_jsonapi.request.request_context import RequestContext


class Resource(metaclass=ABCMeta):
    methods = Methods.values()
    schema: Schema = None
    data_layer: DataLayer = None
    __view_parameters__: dict[str, type] = {}

    @abstractstaticmethod
    def get(cls: Resource, request_ctx: RequestContext):
        raise NotImplementedError

    @abstractstaticmethod
    def post(cls: Resource, request_ctx: RequestContext):
        raise NotImplementedError

    @abstractstaticmethod
    def delete(cls: Resource, request_ctx: RequestContext):
        raise NotImplementedError

    @abstractstaticmethod
    def patch(cls: Resource, request_ctx: RequestContext):
        raise NotImplementedError
