from fastapi_rest_jsonapi.resource import Resource
from fastapi_rest_jsonapi.resource_detail import ResourceDetail


def is_detail_resource(resource: Resource) -> bool:
    return issubclass(resource, ResourceDetail)
