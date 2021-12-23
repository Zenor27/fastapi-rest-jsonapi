from fastapi import FastAPI
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import QueuePool
from fastapi_rest_jsonapi import fields
from fastapi_rest_jsonapi.resource_list import ResourceList

from fastapi_rest_jsonapi.schema import Schema
from fastapi_rest_jsonapi.schema_api import SchemaAPI
from fastapi_rest_jsonapi.sqlachemy_data_layer import SQLAlchemyDataLayer

app = FastAPI()
schema_api = SchemaAPI(app)

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


engine: Engine = create_engine("sqlite:///:memory:", poolclass=QueuePool, connect_args={"check_same_thread": False})
User.metadata.create_all(engine)
session = sessionmaker(bind=engine)()


class UserSchema(Schema):
    __type__ = "user"

    id = fields.Integer()
    name = fields.String()
    age = fields.Integer()


class UserList(ResourceList):
    schema = UserSchema
    data_layer = SQLAlchemyDataLayer(session, User)


def generate_users(COUNT: int = 10):
    for i in range(COUNT):
        user = User(name=f"User {i}", age=i)
        session.add(user)
    session.commit()


generate_users()
schema_api.register(UserList, "/users")
