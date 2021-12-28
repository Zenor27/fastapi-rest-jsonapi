import random
from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response


def test_simple_list(client: TestClient, user, generate_data):
    response: Response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [
            generate_data(user),
        ]
    }


def test_simple_list_multiple_users(client: TestClient, users, generate_data):
    response: Response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [generate_data(user) for user in users]}


def test_simple_detail(client: TestClient, user, generate_data):
    response: Response = client.get(f"/users/{user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": generate_data(user)}


def test_simple_detail_object_not_found(client: TestClient):
    response: Response = client.get("/users/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_simple_detail_multiple_users(client: TestClient, users, generate_data):
    random_user = random.choice(users)
    response: Response = client.get(f"/users/{random_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": generate_data(random_user)}


def test_simple_delete(client: TestClient, user):
    response: Response = client.delete(f"/users/{user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_simple_delete_object_not_found(client: TestClient):
    response: Response = client.delete("/users/42")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_simple_delete_multiple_users(client: TestClient, users):
    random_user = random.choice(users)
    response: Response = client.delete(f"/users/{random_user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_simple_delete_multiple_users_object_not_found(client: TestClient, users):
    response: Response = client.delete("/users/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_simple_update(client: TestClient, user):
    response: Response = client.patch(f"/users/{user.id}", json={"name": "New user name", "age": 24})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_simple_update_multiple_users(client: TestClient, users):
    random_user = random.choice(users)
    response: Response = client.patch(f"/users/{random_user.id}", json={"name": "New user name", "age": 24})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_simple_create_user(client: TestClient):
    response: Response = client.post("/users", json={"name": "New user name", "age": 42})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "data": {
            "type": "user",
            "id": response.json()["data"]["id"],
            "attributes": {"name": "New user name", "age": 42},
        }
    }
