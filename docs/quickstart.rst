.. _quickstart:

Quickstart
==========

Let's write a simple REST API. This guide assumes you have a basic understanding of `FastAPI <https://fastapi.tiangolo.com/>`_, and that you have already installed both FastAPI and FastAPI-REST-JSONAPI.

This small REST API will use SQLAlchemy as datalayer.

You can find an example in the `Git repository <https://github.com/Zenor27/fastapi-rest-jsonapi/tree/main/example>`__.


Initialize the application
--------------------------

Let's create a file `app.py` with the following code.

You first need to initialize the FastAPI application and the REST API.

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_rest_jsonapi.rest_api import RestAPI

    app = FastAPI()
    rest_api = RestAPI(app)

Database model
--------------

Then, let's create our database model.

It will be a simple `User` model with a `name` and an `age`.

.. code-block:: python

    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base

    BaseModel = declarative_base()

    class User(BaseModel):
        __tablename__ = "user"

        id = Column(Integer, primary_key=True)
        name = Column(String)
        age = Column(Integer)


Now, let's create our database engine and fill our database.

For simplicity purpose, we will use a in-memory SQLite database.

.. code-block:: python

    from sqlalchemy.engine.base import Engine
    from sqlalchemy.engine import create_engine
    from sqlalchemy.orm.session import sessionmaker

    engine: Engine = create_engine("sqlite:///:memory:", poolclass=QueuePool, connect_args={"check_same_thread": False})
    User.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    def generate_users(COUNT: int = 10):
        for i in range(COUNT):
            user = User(name=f"User {i}", age=i)
            session.add(user)
        session.commit()

    generate_users()
    

Schema and Resources
--------------------


Now that we are good with the database part, let's create our user API.

We first need to define a schema, it will be the response structure of our API.

.. code-block:: python

    from fastapi_rest_jsonapi.schema import fields, Schema

    class UserSchema(Schema):
        __type__ = "user"

        id = fields.Integer()
        name = fields.String()
        age = fields.Integer()


Then we need to create the resources.

.. code-block:: python

    from fastapi import Path
    from fastapi_rest_jsonapi.resource import ResourceDetail, ResourceList
    from fastapi_rest_jsonapi.data import SQLAlchemyDataLayer

    class UserList(ResourceList):
        schema = UserSchema
        data_layer = SQLAlchemyDataLayer(session, User)


    class UserDetail(ResourceDetail):
        __view_parameters__ = {"id": (int, Path(..., title="id", ge=1))}
        schema = UserSchema
        data_layer = SQLAlchemyDataLayer(session, User)

Resources can be of two types:
    - ResourceList: a list of resources, for example a list of users.
    - ResourceDetail: a single resource, for example a single user.

Resources allow the creation of CRUD operations on a specific model.

On each resource, you need to define the following:
    - the data layer to use, in this case SQLAlchemy.
    - the schema to use, in this case UserSchema.

For a ResourceDetail, you need to define the parameters it can take in the URL.

.. note::

    The `__view_parameters__` must be a dictionary with the following structure:

    .. code-block:: python
    
        {
            "parameter_name": (parameter_type, Path(...)),
        }

    The `Path` object allows you to define validations and more, take a look at the `FastAPI documentation <https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/>`__.


Register
--------

Now we just need to register our resources and give them a URL.

.. code-block:: python

    rest_api.register(UserList, "/users")
    rest_api.register(UserDetail, "/users/{id}")


Let's run the app now.

.. code-block:: console

    $ uvicorn app:app --reload

You should see something like this:

.. code-block:: console

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [81745] using statreload
    INFO:     ✅ Registered GET /users
    INFO:     ✅ Registered POST /users
    INFO:     ✅ Registered GET /users/{id}
    INFO:     ✅ Registered PATCH /users/{id}
    INFO:     ✅ Registered DELETE /users/{id}
    INFO:     Started server process [81747]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.

.. note::

    You can see all the registered routes in the logs.


Now you can go to `http://127.0.0.1:8000/docs <http://127.0.0.1:8000/docs>`__ to test the endpoints in the Swagger.

Congratulations you have a working basic REST API! 🎉