from inspect import Signature, Parameter
from pydantic import BaseModel, create_model
from typing import Optional, Union
from fastapi.applications import FastAPI
from fastapi_rest_jsonapi.methods import Methods
from fastapi_rest_jsonapi.resource_list import ResourceList
from fastapi_rest_jsonapi.schema import Schema
from fastapi_rest_jsonapi import fields


class SchemaAPI:
    METHODS_TO_RESOURCE_FUNCTION = {
        Methods.GET.value: lambda resource: resource.get,
        Methods.POST.value: lambda resource: resource.post,
        Methods.PUT.value: lambda resource: resource.put,
        Methods.DELETE.value: lambda resource: resource.delete,
        Methods.PATCH.value: lambda resource: resource.patch,
    }

    FIELDS_TO_TYPE = {
        fields.Integer: int,
        fields.String: str,
    }

    def __init__(self, app: FastAPI):
        self.app: FastAPI = app

    def __get_method(self, resource: Union[ResourceList, None], method: str):
        return SchemaAPI.METHODS_TO_RESOURCE_FUNCTION[method](resource)

    def __get_response_model(self, schema: Schema, resource_method: str) -> BaseModel:
        fields = {}
        for field_name, field_type in schema._declared_fields.items():
            type_ = SchemaAPI.FIELDS_TO_TYPE.get(type(field_type))
            if type_ is None:
                raise Exception(f"Field {field_name} has no type")
            fields[field_name] = type_

        # For some reasons, FastAPI does not allow to use the same name for the response model
        return create_model(f"{schema.__type__}-{resource_method}", **fields)

    def endpoint_wrapper(self, resource: Union[ResourceList, None], method: str):
        def wrapper(q: Optional[str] = None):
            return self.__get_method(resource, method)(resource, q)

        return wrapper

    def register(self, resource: Union[ResourceList, None], path: str):
        for resource_method in resource.methods:
            self.app.api_route(
                path,
                methods=[resource_method],
                response_model=self.__get_response_model(resource.schema, resource_method),
            )(self.endpoint_wrapper(resource, resource_method))
