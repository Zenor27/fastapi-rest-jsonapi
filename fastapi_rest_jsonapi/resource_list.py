from typing import Optional
from fastapi.responses import JSONResponse
from fastapi_rest_jsonapi.resource import Resource


class ResourceList(Resource):
    @staticmethod
    def get(cls, q: Optional[str] = None):
        objects = cls.data_layer.get()
        return JSONResponse(content=cls.schema().dump(obj=objects, many=True))
