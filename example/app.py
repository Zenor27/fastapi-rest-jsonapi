from fastapi import FastAPI, Path
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import QueuePool
from fastapi_rest_jsonapi.rest_api import RestAPI
from fastapi_rest_jsonapi.schema import fields, Schema
from fastapi_rest_jsonapi.resource import ResourceDetail, ResourceList
from fastapi_rest_jsonapi.data import SQLAlchemyDataLayer

app = FastAPI()
rest_api = RestAPI(app)

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    addresses = relationship("Address", back_populates="user")


class Address(BaseModel):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="addresses")


engine: Engine = create_engine("sqlite:///:memory:", poolclass=QueuePool, connect_args={"check_same_thread": False})
User.metadata.create_all(engine)
Address.metadata.create_all(engine)
session = sessionmaker(bind=engine)()


class UserSchema(Schema):
    __type__ = "user"

    id = fields.Integer()
    name = fields.String()
    age = fields.Integer()
    addresses = fields.Relationship(schema="address", many=True, type_="address")


class UserList(ResourceList):
    schema = UserSchema
    data_layer = SQLAlchemyDataLayer(session, User)


class UserDetail(ResourceDetail):
    __view_parameters__ = {"id": (int, Path(..., title="id", ge=1))}
    schema = UserSchema
    data_layer = SQLAlchemyDataLayer(session, User)


class AddressSchema(Schema):
    __type__ = "address"

    id = fields.Integer()
    name = fields.String()
    user = fields.Relationship(schema="user", type_="user")


class AddressList(ResourceList):
    schema = AddressSchema
    data_layer = SQLAlchemyDataLayer(session, Address)


class AddressDetail(ResourceDetail):
    __view_parameters__ = {"id": (int, Path(..., title="id", ge=1))}
    schema = AddressSchema
    data_layer = SQLAlchemyDataLayer(session, Address)


def generate_users(COUNT: int = 10):
    for i in range(COUNT):
        user = User(name=f"User {i}", age=i)
        session.add(user)
    session.commit()


def generate_addresses():
    for user in session.query(User).all():
        for i in range(2):
            address = Address(name=f"Address {i}", user_id=user.id)
            session.add(address)
    session.commit()


generate_users()
generate_addresses()
rest_api.register(UserList, "/users")
rest_api.register(UserDetail, "/users/{id}")
rest_api.register(AddressList, "/address")
rest_api.register(AddressDetail, "/address/{id}")
