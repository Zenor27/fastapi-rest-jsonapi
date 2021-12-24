from fastapi import status
from fastapi.responses import JSONResponse
from starlette.responses import Response
from fastapi_rest_jsonapi.methods import Methods
from fastapi_rest_jsonapi.request_context import RequestContext
from fastapi_rest_jsonapi.resource import Resource


class ResourceList(Resource):
    methods = [Methods.GET.value, Methods.POST.value]

    @staticmethod
    def get(cls: Resource, request_ctx: RequestContext):
        objects = cls.data_layer.get()
        content = cls.schema().dump(obj=objects, many=True)
        return JSONResponse(content=content)

    @staticmethod
    def post(cls: Resource, request_ctx: RequestContext):
        created = cls.data_layer.create_one(**request_ctx.body)
        if created is None:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        content = cls.schema().dump(obj=created, many=False)
        return JSONResponse(content=content, status_code=status.HTTP_201_CREATED)
