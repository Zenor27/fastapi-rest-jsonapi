from pytest import fixture
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_rest_jsonapi import SchemaAPI


@fixture()
def app() -> FastAPI:
    app: FastAPI = FastAPI()
    return app


@fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@fixture()
def schema_api(app: FastAPI) -> SchemaAPI:
    schema_api: SchemaAPI = SchemaAPI(app)
    return schema_api
