from fastapi import status
from fastapi_rest_jsonapi.resource import Resource
from fastapi_rest_jsonapi.common.methods import Methods
from fastapi_rest_jsonapi.request.request_context import RequestContext
from fastapi_rest_jsonapi.response.response import Response


DEFAULT_PAGE_SIZE = 30


class ResourceList(Resource):
    methods = [Methods.GET.value, Methods.POST.value]
    page_size = DEFAULT_PAGE_SIZE

    @staticmethod
    def get(cls: Resource, request_ctx: RequestContext):
        request_ctx_page = request_ctx.page
        if request_ctx_page.size is None:
            request_ctx_page.size = cls.page_size

        objects = cls.data_layer.get(request_ctx.sorts, request_ctx.fields, request_ctx_page)
        content = cls.schema().dump(obj=objects, many=True)
        return Response(request_ctx, content=content)

    @staticmethod
    def post(cls: Resource, request_ctx: RequestContext):
        created = cls.data_layer.create_one(**request_ctx.body)
        if created is None:
            return Response(request_ctx, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        content = cls.schema().dump(obj=created, many=False)
        return Response(request_ctx, content=content, status_code=status.HTTP_201_CREATED)
