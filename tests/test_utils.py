from pytest import fixture
from fastapi import Path
from fastapi_rest_jsonapi.schema import fields, Schema
from fastapi_rest_jsonapi.resource import ResourceList, ResourceDetail
from fastapi_rest_jsonapi.resource.utils import is_detail_resource


@fixture()
def user_schema():
    class UserSchema(Schema):
        __type__ = "user"

        id = fields.Integer()
        name = fields.String()
        age = fields.Integer()

    yield UserSchema


@fixture()
def user_list(user_schema):
    class UserList(ResourceList):
        schema = user_schema

    yield UserList


@fixture()
def user_detail(user_schema):
    class UserDetail(ResourceDetail):
        __view_parameters__ = {"id": (int, Path(..., title="id", ge=1))}
        schema = user_schema

    yield UserDetail


def test_is_detail_resource(user_detail):
    assert is_detail_resource(user_detail)


def test_is_not_detail_resource(user_list):
    assert not is_detail_resource(user_list)
