from pytest import fixture
from fastapi.testclient import TestClient
from requests.models import Response
from sqlalchemy import Column, Integer, String
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from fastapi_rest_jsonapi import SchemaAPI
from fastapi_rest_jsonapi import fields
from fastapi_rest_jsonapi.resource_list import ResourceList
from fastapi_rest_jsonapi.schema import Schema
from fastapi_rest_jsonapi.sqlachemy_data_layer import SQLAlchemyDataLayer


@fixture(scope="module")
def model_base():
    return declarative_base()


@fixture(scope="module")
def user_model(model_base):
    class User(model_base):
        __tablename__ = "user"

        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)

    return User


@fixture(scope="module")
def engine(user_model) -> Engine:
    engine: Engine = create_engine("sqlite:///:memory:", poolclass=QueuePool, connect_args={"check_same_thread": False})
    user_model.metadata.create_all(engine)
    return engine


@fixture(scope="module")
def session(engine: Engine) -> Session:
    Session = sessionmaker(bind=engine)
    return Session()


@fixture()
def user(session: Session, user_model):
    user = user_model(name="John", age=42)
    session.add(user)
    session.commit()
    return user


@fixture(scope="module")
def user_schema():
    class UserSchema(Schema):
        __type__ = "user"

        id = fields.Integer()
        name = fields.String()
        age = fields.Integer()

    return UserSchema


@fixture(scope="module")
def user_list(user_schema, session: Session, user_model):
    class UserList(ResourceList):
        schema = user_schema
        data_layer = SQLAlchemyDataLayer(session, user_model)

    return UserList


@fixture(scope="module")
def register_schema_routes(schema_api: SchemaAPI, user_list):
    schema_api.register(user_list, "/users")


def test_simple_list(register_schema_routes, user, client: TestClient):
    response: Response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == {"data": [{"type": "user", "id": 1, "attributes": {"name": "John", "age": 42}}]}
