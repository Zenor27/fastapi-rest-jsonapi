from fastapi import status
from fastapi.testclient import TestClient


def test_create_uniq_key(client: TestClient, users):
    response = client.post(
        "/users",
        json={
            "data": {
                "type": "user",
                "attributes": {"name": "John", "age": 25, "id": users[0].id},
            }
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
