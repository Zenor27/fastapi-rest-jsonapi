from typing import Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi_rest_jsonapi.methods import Methods
from fastapi_rest_jsonapi.resource import Resource


class ResourceList(Resource):
    methods = [Methods.GET.value, Methods.POST.value]

    @staticmethod
    def get(cls: Resource, parameters: Optional[BaseModel] = None):
        objects = cls.data_layer.get()
        content = cls.schema().dump(obj=objects, many=True)
        return JSONResponse(content=content)
