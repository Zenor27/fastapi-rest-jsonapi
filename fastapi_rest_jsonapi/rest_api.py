from logging import Logger, getLogger
from typing import List, Optional
from pydantic import BaseModel, create_model
from fastapi import Depends, Body, Request
from fastapi.applications import FastAPI
from fastapi.exceptions import HTTPException
from fastapi_rest_jsonapi.common import Methods
from fastapi_rest_jsonapi.schema import fields, Schema
from fastapi_rest_jsonapi.request.request_context import RequestContext
from fastapi_rest_jsonapi.resource import Resource
from fastapi_rest_jsonapi.resource.utils import is_detail_resource


class RestAPI:
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

    QUERY_PARAMETER_KEYS = ["sort", "field", "page"]

    def __init__(self, app: FastAPI, logger: Logger = None):
        self.app: FastAPI = app
        if logger is None:
            self.logger = getLogger("uvicorn.error")
        else:
            self.logger = logger

        self.registered_resources: list[(Resource, str)] = []
        self.app.on_event("startup")(self.__on_app_startup)

    def __on_app_startup(self, *_, **__):
        self.__override_swagger_doc()
        self.logger.info("✅ REST API is ready")

    def __get_method(self, resource: Resource, method: str):
        return RestAPI.METHODS_TO_RESOURCE_FUNCTION[method](resource)

    def __get_schema_fields(self, schema: Schema) -> dict[str, tuple[type, ...]]:
        fields = {}
        for field_name, field_type in schema._declared_fields.items():
            type_ = RestAPI.FIELDS_TO_TYPE.get(type(field_type))
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
        return create_model(
            f"{resource.schema.__type__}-{method}-path-parameters",
            **resource.__view_parameters__,
        )

    def __get_endpoint_summary(self, resource: Resource, method: str) -> str:
        is_detail_resource_ = is_detail_resource(resource)
        schema_type = resource.schema.__type__
        return (
            f"{method} {'a' if is_detail_resource_ else 'multiple'} {schema_type}{'' if is_detail_resource_ else 's'}"
        )

    def __get_query_parameters_dict(self, request: Request) -> dict:
        request_query_params_dict = request.query_params._dict

        def __get_query_params_with_brackets(query_param_name: str):
            if query_param_name == "sort":
                return request_query_params_dict.get(query_param_name)

            # Handle swagger that write query parameters with brackets as parameter=parameter[...]=somevalue
            if request_query_param := request_query_params_dict.get(query_param_name):
                return request_query_param.split("&")

            return [f"{k}={v}" for k, v in request_query_params_dict.items() if query_param_name in k]

        return {parameter: __get_query_params_with_brackets(parameter) for parameter in RestAPI.QUERY_PARAMETER_KEYS}

    def __override_swagger_doc(self):
        def __generate_field_parameter(field_name: str) -> dict:
            return {
                "in": "query",
                "name": field_name,
                "style": "deepObject",
                "explode": True,
            }

        openapi = self.app.openapi()
        for resource, resource_url in self.registered_resources:
            if Methods.GET.value not in resource.methods or is_detail_resource(resource):
                continue
            openapi["paths"][resource_url]["get"]["parameters"] = [
                *[__generate_field_parameter(field_name) for field_name in RestAPI.QUERY_PARAMETER_KEYS]
            ]

    def endpoint_wrapper(self, resource: Resource, method: str):
        def endpoint(request: Request, path_parameters, body):
            try:
                request_ctx = RequestContext(
                    url=request.url,
                    path_parameters=path_parameters,
                    query_parameters=self.__get_query_parameters_dict(request),
                    body=body,
                )
                return self.__get_method(resource, method)(resource, request_ctx)
            except (ValueError, AttributeError) as exc:
                self.logger.error(exc)
                raise HTTPException(status_code=500, detail="Internal server error")

        # GET method cannot have body parameter in Swagger UI... So we need to have a different wrapper
        if method in [Methods.DELETE.value, Methods.PATCH.value, Methods.POST.value]:

            def wrapper(
                request: Request,
                path_parameters: self.__get_path_parameters_model(resource, method) = Depends(),
                body: Optional[dict] = Body(default=None),
            ):
                return endpoint(request, path_parameters, body)

        else:

            def wrapper(
                request: Request,
                path_parameters: self.__get_path_parameters_model(resource, method) = Depends(),
            ):
                return endpoint(request, path_parameters, None)

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
                tags=[resource.schema.__type__],
            )(self.endpoint_wrapper(resource, method))
            self.registered_resources.append((resource, path))
            self.logger.info(f"✅ Registered {method} {path}")
