from pytest import fixture
from fastapi import Path
from sqlalchemy import Column, Integer, String
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from fastapi_rest_jsonapi import RestAPI
from fastapi_rest_jsonapi.data import SQLAlchemyDataLayer
from fastapi_rest_jsonapi.schema import fields, Schema
from fastapi_rest_jsonapi.resource import ResourceDetail, ResourceList


@fixture()
def model_base():
    yield declarative_base()


@fixture()
def user_model(model_base):
    class User(model_base):
        __tablename__ = "user"

        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)

    yield User


@fixture()
def engine(user_model) -> Engine:
    engine: Engine = create_engine(
        "sqlite:///:memory:",
        poolclass=QueuePool,
        connect_args={"check_same_thread": False},
    )
    user_model.metadata.create_all(engine)
    yield engine


@fixture()
def session(engine: Engine) -> Session:
    Session = sessionmaker(bind=engine)
    yield Session()


@fixture()
def user(session: Session, user_model):
    user = user_model(name="John", age=42)
    session.add(user)
    session.commit()
    yield user


@fixture()
def user_count():
    return 60


@fixture()
def users(session: Session, user_model, user_count):
    users = []
    for i in range(user_count, 0, -1):
        user = user_model(name=f"John {i}", age=i)
        users.append(user)
        session.add(user)
    session.commit()
    yield users


@fixture()
def user_schema():
    class UserSchema(Schema):
        __type__ = "user"

        id = fields.Integer()
        name = fields.String()
        age = fields.Integer()

    yield UserSchema


@fixture()
def user_list(user_schema, session: Session, user_model):
    class UserList(ResourceList):
        schema = user_schema
        data_layer = SQLAlchemyDataLayer(session, user_model)
        page_size = 0

    yield UserList


@fixture()
def user_detail(user_schema, session: Session, user_model):
    class UserDetail(ResourceDetail):
        __view_parameters__ = {"id": (int, Path(..., title="id", ge=1))}
        schema = user_schema
        data_layer = SQLAlchemyDataLayer(session, user_model)

    yield UserDetail


@fixture(autouse=True)
def register_schema_routes(rest_api: RestAPI, user_list, user_detail):
    rest_api.register(user_list, "/users")
    rest_api.register(user_detail, "/users/{id}")


@fixture()
def generate_data():
    def _generate_data(user, only_fields=None):
        if only_fields is not None:
            attributes = {field: getattr(user, field) for field in only_fields}
        else:
            attributes = {
                "name": user.name,
                "age": user.age,
            }
        return {"type": "user", "id": user.id, "attributes": attributes}

    return _generate_data
