from fastapi import status


class RestAPIException(Exception):
    """
    Base class for all REST API exceptions.
    """

    status = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal Server Error"


class UnknownRelationshipException(RestAPIException):
    def __init__(self, relationship: str):
        self.status = status.HTTP_400_BAD_REQUEST
        self.message = f"Unknown relationship: {relationship}"


class UnknownTypeException(RestAPIException):
    def __init__(self, type_: str):
        self.status = status.HTTP_400_BAD_REQUEST
        self.message = f"Unknown type: {type_}"


class UnknownFieldException(RestAPIException):
    def __init__(self, field: str):
        self.status = status.HTTP_400_BAD_REQUEST
        self.message = f"Unknown field: {field}"


class UnknownSchemaException(RestAPIException):
    def __init__(self, schema: str):
        self.status = status.HTTP_400_BAD_REQUEST
        self.message = f"Unknown schema: {schema}"
