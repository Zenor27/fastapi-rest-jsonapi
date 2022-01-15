from math import ceil
from fastapi import status
from fastapi.testclient import TestClient
from requests.models import Response


def generate_links(
    current_page_number: int, current_page_size: int, has_prev_page: bool, has_next_page: bool, user_count: int
) -> dict:
    last_page = ceil(user_count / current_page_size)
    return {
        "first": f"http://testserver/users?page%5Bnumber%5D={1}&page%5Bsize%5D={current_page_size}",
        "last": f"http://testserver/users?page%5Bnumber%5D={last_page}&page%5Bsize%5D={current_page_size}",
        "next": f"http://testserver/users?page%5Bnumber%5D={current_page_number + 1}&page%5Bsize%5D={current_page_size}"
        if has_next_page
        else None,
        "prev": f"http://testserver/users?page%5Bnumber%5D={current_page_number - 1}&page%5Bsize%5D={current_page_size}"
        if has_prev_page
        else None,
        "self": f"http://testserver/users?page%5Bnumber%5D={current_page_number}&page%5Bsize%5D={current_page_size}",
    }


def test_simple_default_pagination_first_page(client: TestClient, users, generate_data, user_count):
    response: Response = client.get("/users?page[number]=1&page[size]=30")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [generate_data(user) for user in users[:30]],
        "links": generate_links(1, 30, False, True, user_count),
    }


def test_simple_default_pagination_second_page(client: TestClient, users, generate_data, user_count):
    response: Response = client.get("/users?page[number]=2&page[size]=30")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [generate_data(user) for user in users[30:60]],
        "links": generate_links(2, 30, True, False, user_count),
    }


def test_disable_pagination(client: TestClient, users, generate_data):
    response: Response = client.get("/users?page[size]=0")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [generate_data(user) for user in users]}


def test_wrong_page(client: TestClient, users, generate_data, user_count):
    response: Response = client.get("/users?page[number]=424242&page[size]=30")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"data": [], "links": generate_links(424242, 30, True, False, user_count)}
