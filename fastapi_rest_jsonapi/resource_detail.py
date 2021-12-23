from typing import Optional
from pydantic import BaseModel
from fastapi import status
from fastapi.responses import JSONResponse, Response
from fastapi_rest_jsonapi.methods import Methods
from fastapi_rest_jsonapi.resource import Resource


class ResourceDetail(Resource):
    methods = [Methods.GET.value, Methods.PATCH.value, Methods.DELETE.value]

    @staticmethod
    def get(cls: Resource, parameters: Optional[BaseModel] = None):
        object = cls.data_layer.get_one(parameters.id)
        return JSONResponse(content=cls.schema().dump(obj=object, many=False))

    @staticmethod
    def delete(cls: Resource, parameters: Optional[BaseModel] = None):
        is_deleted = cls.data_layer.delete_one(parameters.id)
        if is_deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
