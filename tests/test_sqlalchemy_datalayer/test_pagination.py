from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response


def test_simple_default_pagination_first_page(client: TestClient, users, generate_data):
    response: Response = client.get("/users?page%5Bnumber%5D=1&page%5Bsize%5D=30")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [generate_data(user) for user in users[:30]]}


def test_simple_default_pagination_second_page(client: TestClient, users, generate_data):
    response: Response = client.get("/users?page%5Bnumber%5D=2&page%5Bsize%5D=30")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [generate_data(user) for user in users[30:60]]}


def test_disable_pagination(client: TestClient, users, generate_data):
    response: Response = client.get("/users?page%5Bsize%5D=0")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [generate_data(user) for user in users]}
