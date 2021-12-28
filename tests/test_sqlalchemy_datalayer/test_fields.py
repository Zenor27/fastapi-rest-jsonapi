from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response


def test_simple_fields(client: TestClient, users, generate_data):
    response: Response = client.get("/users?field%5Buser%5D=age")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [generate_data(user, only_fields=["age"]) for user in users]}


def test_two_fields(client: TestClient, users, generate_data):
    response: Response = client.get("/users?field%5Buser%5D=age,name")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [generate_data(user, only_fields=["age", "name"]) for user in users]}


def test_non_existing_field(client: TestClient, users):
    response: Response = client.get("/users?field%5Buser%5D=broken")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_non_existing_type(client: TestClient, users):
    response: Response = client.get("/users?field%5Bfoobar%5D=age")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
