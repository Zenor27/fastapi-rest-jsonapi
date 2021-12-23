from enum import Enum
from fastapi_rest_jsonapi.enum import EnumMeta


class Methods(Enum, metaclass=EnumMeta):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"