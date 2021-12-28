from pytest import fixture
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_rest_jsonapi import RestAPI


@fixture()
def app() -> FastAPI:
    app: FastAPI = FastAPI()
    return app


@fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@fixture()
def rest_api(app: FastAPI) -> RestAPI:
    rest_api: RestAPI = RestAPI(app)
    return rest_api
