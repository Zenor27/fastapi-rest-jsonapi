from typing import Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi_rest_jsonapi.methods import Methods
from fastapi_rest_jsonapi.resource import Resource


class ResourceDetail(Resource):
    methods = [Methods.GET.value, Methods.PATCH.value, Methods.DELETE.value]

    @staticmethod
    def get(cls: Resource, parameters: Optional[BaseModel] = None):
        object = cls.data_layer.get_one(parameters.id)
        return JSONResponse(content=cls.schema().dump(obj=object, many=False))
