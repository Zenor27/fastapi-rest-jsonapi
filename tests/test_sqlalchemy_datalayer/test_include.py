from fastapi import status
from requests.models import Response
from fastapi.testclient import TestClient


def test_simple_include(client: TestClient, articles, comments):
    response: Response = client.get("/articles/1?include=comments")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": {
            "type": "article",
            "id": 1,
            "attributes": {"name": "Article 0", "price": 0},
            "relationships": {"comments": {"data": [{"id": 1, "type": "comment"}, {"id": 2, "type": "comment"}]}},
        },
        "included": [
            {"type": "comment", "id": 1, "attributes": {"text": "comment 0", "author_id": 1}},
            {"type": "comment", "id": 2, "attributes": {"text": "comment 1", "author_id": 2}},
        ],
    }


def test_include_list(client: TestClient, articles, comments):
    response: Response = client.get("/articles?include=comments")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": [
            {
                "type": "article",
                "attributes": {"name": "Article 0", "price": 0},
                "id": 1,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 1}, {"type": "comment", "id": 2}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 1", "price": 1},
                "id": 2,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 3}, {"type": "comment", "id": 4}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 2", "price": 2},
                "id": 3,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 5}, {"type": "comment", "id": 6}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 3", "price": 3},
                "id": 4,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 7}, {"type": "comment", "id": 8}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 4", "price": 4},
                "id": 5,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 9}, {"type": "comment", "id": 10}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 5", "price": 5},
                "id": 6,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 11}, {"type": "comment", "id": 12}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 6", "price": 6},
                "id": 7,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 13}, {"type": "comment", "id": 14}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 7", "price": 7},
                "id": 8,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 15}, {"type": "comment", "id": 16}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 8", "price": 8},
                "id": 9,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 17}, {"type": "comment", "id": 18}]}},
            },
            {
                "type": "article",
                "attributes": {"name": "Article 9", "price": 9},
                "id": 10,
                "relationships": {"comments": {"data": [{"type": "comment", "id": 19}, {"type": "comment", "id": 20}]}},
            },
        ],
        "included": [
            {"type": "comment", "attributes": {"text": "comment 0", "author_id": 1}, "id": 1},
            {"type": "comment", "attributes": {"text": "comment 1", "author_id": 2}, "id": 2},
            {"type": "comment", "attributes": {"text": "comment 2", "author_id": 3}, "id": 3},
            {"type": "comment", "attributes": {"text": "comment 3", "author_id": 4}, "id": 4},
            {"type": "comment", "attributes": {"text": "comment 4", "author_id": 5}, "id": 5},
            {"type": "comment", "attributes": {"text": "comment 5", "author_id": 6}, "id": 6},
            {"type": "comment", "attributes": {"text": "comment 6", "author_id": 7}, "id": 7},
            {"type": "comment", "attributes": {"text": "comment 7", "author_id": 8}, "id": 8},
            {"type": "comment", "attributes": {"text": "comment 8", "author_id": 9}, "id": 9},
            {"type": "comment", "attributes": {"text": "comment 9", "author_id": 10}, "id": 10},
            {"type": "comment", "attributes": {"text": "comment 10", "author_id": 11}, "id": 11},
            {"type": "comment", "attributes": {"text": "comment 11", "author_id": 12}, "id": 12},
            {"type": "comment", "attributes": {"text": "comment 12", "author_id": 13}, "id": 13},
            {"type": "comment", "attributes": {"text": "comment 13", "author_id": 14}, "id": 14},
            {"type": "comment", "attributes": {"text": "comment 14", "author_id": 15}, "id": 15},
            {"type": "comment", "attributes": {"text": "comment 15", "author_id": 16}, "id": 16},
            {"type": "comment", "attributes": {"text": "comment 16", "author_id": 17}, "id": 17},
            {"type": "comment", "attributes": {"text": "comment 17", "author_id": 18}, "id": 18},
            {"type": "comment", "attributes": {"text": "comment 18", "author_id": 19}, "id": 19},
            {"type": "comment", "attributes": {"text": "comment 19", "author_id": 20}, "id": 20},
        ],
    }


def test_simple_include_with_fields(client: TestClient, articles, comments):
    response: Response = client.get("/articles/1?include=comments&fields[comment]=text&fields[article]=name,comments")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": {
            "type": "article",
            "id": 1,
            "attributes": {"name": "Article 0"},
            "relationships": {"comments": {"data": [{"id": 1, "type": "comment"}, {"id": 2, "type": "comment"}]}},
        },
        "included": [
            {"type": "comment", "id": 1, "attributes": {"text": "comment 0"}},
            {"type": "comment", "id": 2, "attributes": {"text": "comment 1"}},
        ],
    }


def test_simple_include_with_fields_no_relationship(client: TestClient, articles, comments):
    response: Response = client.get("/articles/1?include=comments&fields[comment]=text&fields[article]=name")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": {
            "type": "article",
            "id": 1,
            "attributes": {"name": "Article 0"},
        },
        "included": [
            {"type": "comment", "id": 1, "attributes": {"text": "comment 0"}},
            {"type": "comment", "id": 2, "attributes": {"text": "comment 1"}},
        ],
    }


def test_simple_include_with_fields_no_include(client: TestClient, articles, comments):
    response: Response = client.get("/articles/1?fields[article]=name,comments")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "data": {
            "type": "article",
            "id": 1,
            "attributes": {"name": "Article 0"},
            "relationships": {"comments": {"data": [{"id": 1, "type": "comment"}, {"id": 2, "type": "comment"}]}},
        },
    }


def test_simple_include_with_fields_no_include_bad_field(client: TestClient, articles, comments):
    response: Response = client.get("/articles/1?fields[comment]=text&fields[article]=name,comments")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_non_exisiting_include(client: TestClient, articles, comments):
    response: Response = client.get("/articles/1?include=foobar")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
