from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response


def test_simple_sorting(client: TestClient, users, generate_data):
    response: Response = client.get("/users?sort=age")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [
            generate_data(user) for user in sorted(users, key=lambda user: user.age)
        ]
    }


def test_simple_sorting_desc(client: TestClient, users, generate_data):
    response: Response = client.get("/users?sort=-age")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [
            generate_data(user)
            for user in sorted(users, key=lambda user: user.age, reverse=True)
        ]
    }


def test_sorting_multiple_fields(client: TestClient, users, generate_data):
    response: Response = client.get("/users?sort=age,name")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [
            generate_data(user)
            for user in sorted(users, key=lambda user: (user.age, user.name))
        ]
    }


def test_sorting_multiple_fields_desc(client: TestClient, users, generate_data):
    response: Response = client.get("/users?sort=-age,name")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [
            generate_data(user)
            for user in sorted(
                users, key=lambda user: (user.age, user.name), reverse=True
            )
        ]
    }


def test_sorting_non_existing_field(client: TestClient, users, generate_data):
    response: Response = client.get("/users?sort=foobar")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
