from __future__ import annotations
from abc import ABC

from fastapi import status
from fastapi_rest_jsonapi.common import Methods
from fastapi_rest_jsonapi.resource import Resource
from fastapi_rest_jsonapi.request.request_context import RequestContext
from fastapi_rest_jsonapi.response.response import Response


class ResourceDetail(Resource, ABC):
    methods = [Methods.GET.value, Methods.PATCH.value, Methods.DELETE.value]

    @staticmethod
    def get(cls: Resource, request_ctx: RequestContext):
        obj = cls.data_layer.get_one(request_ctx.path_parameters.id, request_ctx.fields, request_ctx.includes)
        if obj is None:
            return Response(request_ctx, status_code=status.HTTP_404_NOT_FOUND)
        return Response(
            request_ctx,
            content=cls.schema().dump(includes=request_ctx.includes, fields=request_ctx.fields, obj=obj, many=False),
        )

    @staticmethod
    def delete(cls: Resource, request_ctx: RequestContext):
        is_deleted = cls.data_layer.delete_one(request_ctx.path_parameters.id)
        if is_deleted:
            return Response(request_ctx, status_code=status.HTTP_204_NO_CONTENT)
        return Response(request_ctx, status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def patch(cls: Resource, request_ctx: RequestContext):
        is_updated = cls.data_layer.update_one(request_ctx.path_parameters.id, **request_ctx.body) is not None
        if is_updated:
            return Response(request_ctx, status_code=status.HTTP_204_NO_CONTENT)
        return Response(request_ctx, status_code=status.HTTP_404_NOT_FOUND)
