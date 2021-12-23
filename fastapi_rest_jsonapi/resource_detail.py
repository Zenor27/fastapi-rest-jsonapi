from typing import Optional
from pydantic import BaseModel
from fastapi import status
from fastapi.responses import JSONResponse, Response
from fastapi_rest_jsonapi.methods import Methods
from fastapi_rest_jsonapi.request_context import RequestContext
from fastapi_rest_jsonapi.resource import Resource


class ResourceDetail(Resource):
    methods = [Methods.GET.value, Methods.PATCH.value, Methods.DELETE.value]

    @staticmethod
    def get(cls: Resource, request_ctx: RequestContext):
        object = cls.data_layer.get_one(request_ctx.path_parameters.id)
        if object is None:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return JSONResponse(content=cls.schema().dump(obj=object, many=False))

    @staticmethod
    def delete(cls: Resource, request_ctx: RequestContext):
        is_deleted = cls.data_layer.delete_one(request_ctx.path_parameters.id)
        if is_deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def patch(cls: Resource, request_ctx: RequestContext):
        is_updated = cls.data_layer.update_one(request_ctx.path_parameters.id, **request_ctx.body) is not None
        if is_updated:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return Response(status_code=status.HTTP_404_NOT_FOUND)
