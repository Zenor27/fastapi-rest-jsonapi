from fastapi_rest_jsonapi.resource import Resource, ResourceDetail


def is_detail_resource(resource: Resource) -> bool:
    return issubclass(resource, ResourceDetail)
