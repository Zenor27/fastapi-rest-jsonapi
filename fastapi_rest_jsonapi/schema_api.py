from logging import Logger, getLogger
from typing import List, Optional
from pydantic import BaseModel, create_model
from fastapi import Depends, Body
from fastapi.applications import FastAPI
from fastapi_rest_jsonapi.methods import Methods
from fastapi_rest_jsonapi.request_context import RequestContext
from fastapi_rest_jsonapi.resource import Resource
from fastapi_rest_jsonapi import fields
from fastapi_rest_jsonapi.schema import Schema
from fastapi_rest_jsonapi.utils import is_detail_resource


class SchemaAPI:
    METHODS_TO_RESOURCE_FUNCTION = {
        Methods.GET.value: lambda resource: resource.get,
        Methods.POST.value: lambda resource: resource.post,
        Methods.DELETE.value: lambda resource: resource.delete,
        Methods.PATCH.value: lambda resource: resource.patch,
    }

    FIELDS_TO_TYPE = {
        fields.Integer: int,
        fields.String: str,
    }

    def __init__(self, app: FastAPI, logger: Logger = None):
        self.app: FastAPI = app
        if logger is None:
            self.logger = getLogger("uvicorn.error")
        else:
            self.logger = logger

    def __get_method(self, resource: Resource, method: str):
        return SchemaAPI.METHODS_TO_RESOURCE_FUNCTION[method](resource)

    def __get_schema_fields(self, schema: Schema) -> dict[str, tuple[type, ...]]:
        fields = {}
        for field_name, field_type in schema._declared_fields.items():
            type_ = SchemaAPI.FIELDS_TO_TYPE.get(type(field_type))
            if type_ is None:
                raise Exception(f"Field {field_name} has no type")
            fields[field_name] = (type_, None)
        return fields

    def __get_response_model(self, resource: Resource, method: str) -> BaseModel:
        schema = resource.schema
        fields = self.__get_schema_fields(schema)
        is_detail_resource_ = is_detail_resource(resource)
        model_suffix = "detail" if is_detail_resource_ else "list"
        # For some reasons, FastAPI does not allow to use the same name for the response model
        response_model = create_model(f"{schema.__type__}-{method}-{model_suffix}", **fields)
        if is_detail_resource_:
            return response_model
        return List[response_model]

    def __get_path_parameters_model(self, resource: Resource, method: str) -> BaseModel:
        return create_model(f"{resource.schema.__type__}-{method}-path-parameters", **resource.__view_parameters__)

    def __get_endpoint_summary(self, resource: Resource, method: str) -> str:
        is_detail_resource_ = is_detail_resource(resource)
        return f"{method} {'a' if is_detail_resource_ else 'multiple'} {resource.schema.__type__}{'' if is_detail_resource_ else 's'}"

    def endpoint_wrapper(self, resource: Resource, method: str):
        if method in [Methods.PATCH.value, Methods.POST.value]:

            def wrapper(
                path_parameters: self.__get_path_parameters_model(resource, method) = Depends(),
                q: Optional[str] = None,
                body: Optional[dict] = Body(default=None),
            ):
                request_ctx = RequestContext(path_parameters=path_parameters, query_parameters=q, body=body)
                return self.__get_method(resource, method)(resource, request_ctx)

        else:

            def wrapper(
                path_parameters: self.__get_path_parameters_model(resource, method) = Depends(),
                q: Optional[str] = None,
            ):
                request_ctx = RequestContext(path_parameters=path_parameters, query_parameters=q, body=None)
                return self.__get_method(resource, method)(resource, request_ctx)

        return wrapper

    def register(self, resource: Resource, path: str):
        for method in resource.methods:
            response_model = None
            if method not in [Methods.DELETE.value, Methods.PATCH.value]:
                response_model = self.__get_response_model(resource, method)
            self.app.api_route(
                path,
                methods=[method],
                summary=self.__get_endpoint_summary(resource, method),
                response_model=response_model,
            )(self.endpoint_wrapper(resource, method))
            self.logger.info(f"✅ Registered {method} {path}")
