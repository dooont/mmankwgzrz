from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest

from data.people import NAME

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

#testing the hello endpoint
def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json

#testing the title endpoint
def test_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    print(f'{ep.TITLE_EP=}')
    resp_json = resp.get_json()
    print(f'{resp_json=}')
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)
    assert len(resp_json[ep.TITLE_RESP]) > 0

#testing the repository name endpoint
def test_repo_name():
    resp = TEST_CLIENT.get(ep.REPO_NAME_EP)
    print(f'{ep.REPO_NAME_EP=}')
    resp_json = resp.get_json()
    print(f'{resp_json=}')
    assert ep.REPO_NAME_RESP in resp_json
    assert isinstance(resp_json[ep.REPO_NAME_RESP], str)
    assert len(resp_json[ep.REPO_NAME_RESP]) > 0

#testing the people endpoint
def test_get_people():
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    print(f'{ep.PEOPLE_EP=}')
    resp_json = resp.get_json()
    print(f'{resp_json=}')
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person