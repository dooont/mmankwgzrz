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



# testing the hello endpoint
def test_get_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


# testing the title endpoint
def test_get_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    print(f'{ep.TITLE_EP=}')
    resp_json = resp.get_json()
    print(f'{resp_json=}')
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)
    assert len(resp_json[ep.TITLE_RESP]) > 0


# testing the repository name endpoint
def test_get_repo_name():
    resp = TEST_CLIENT.get(ep.REPO_NAME_EP)
    print(f'{ep.REPO_NAME_EP=}')
    resp_json = resp.get_json()
    print(f'{resp_json=}')
    assert ep.REPO_NAME_RESP in resp_json
    assert isinstance(resp_json[ep.REPO_NAME_RESP], str)
    assert len(resp_json[ep.REPO_NAME_RESP]) > 0


@patch('data.people.read', autospec=True,
       return_value={'id': {NAME: 'Joe Schmoe'}})
def test_read(mock_read):
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person
        

@patch('data.people.read_one', autospec=True,
       return_value={NAME: 'Joe Schmoe'})
def test_read_one(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == OK


@patch('data.people.read_one', autospec=True, return_value=None)
def test_read_one_not_found(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == NOT_FOUND

    
# testing the people endpoint
def test_get_people():
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    print(f'{ep.PEOPLE_EP=}')
    resp_json = resp.get_json()
    print(f'{resp_json=}')
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person


def test_people_create_form():
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/create/form')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.PEOPLE_CREATE_FORM in resp_json
    form_data = resp_json[ep.PEOPLE_CREATE_FORM]
    assert isinstance(form_data, dict)
    assert ep.ppl.NAME in form_data
    assert ep.ppl.EMAIL in form_data
    assert ep.ppl.AFFILIATION in form_data
    # assert ep.ppl.ROLES in form_data
    assert form_data[ep.ppl.NAME] == "string"
    assert form_data[ep.ppl.EMAIL] == "string"
    assert form_data[ep.ppl.AFFILIATION] == "string"
    # assert form_data[ep.ppl.ROLES] == "list of strings"


def test_update_person():
    test_email = "ejc369@nyu.edu"
    update_data = {
        ep.ppl.NAME: "Updated Name",
        ep.ppl.AFFILIATION: "New Affiliation",
        ep.ppl.ROLES: ["AU", "CE"]
    }

    # Success case
    with patch('data.people.read_one') as mock_read_one, \
         patch('data.people.update', return_value=update_data) as mock_update:
        # Mock that person exists
        mock_read_one.return_value = {"email": test_email}  
        
        resp = TEST_CLIENT.put(
            f'{ep.PEOPLE_EP}/{test_email}',
            json=update_data
        )

        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert ep.MESSAGE in resp_json
        assert ep.RETURN in resp_json
        assert resp_json[ep.RETURN] == update_data
        mock_read_one.assert_called_once_with(test_email)
        mock_update.assert_called_once()

    # Nonexistent email case
    with patch('data.people.read_one', return_value=None):
        resp = TEST_CLIENT.put(
            f'{ep.PEOPLE_EP}/nonexistent@nyu.edu',
            json=update_data
        )
        assert resp.status_code == NOT_FOUND

    # Invalid data case
    with patch('data.people.read_one') as mock_read_one:
        mock_read_one.return_value = {"email": test_email}  
        invalid_data = {
            ep.ppl.NAME: "",  # invalid empty name
            ep.ppl.AFFILIATION: "",
            ep.ppl.ROLES: ["nonexistent_role"]  # invalid role
        }
        resp = TEST_CLIENT.put(
            f'{ep.PEOPLE_EP}/{test_email}',
            json=invalid_data
        )
        assert resp.status_code == NOT_ACCEPTABLE


@patch('data.people.exists', autospec=True)
@patch('data.people.create', autospec=True, return_value="test@nyu.edu")
def test_create_person(mock_create, mock_exists):
    mock_exists.return_value = False  # assume person doesn't exist yet
    
    test_data = {
        ep.ppl.NAME: "Test Person",
        ep.ppl.EMAIL: "test@nyu.edu",
        ep.ppl.AFFILIATION: "NYU",
        ep.ppl.ROLES: "AU"
    }
    
    resp = TEST_CLIENT.put(f'{ep.PEOPLE_EP}/create', json=test_data)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json
    assert resp_json[ep.RETURN] == "test@nyu.edu"
    
    mock_exists.assert_called_once_with("test@nyu.edu")
    mock_create.assert_called_once()


@patch('data.people.exists', autospec=True)
@patch('data.people.create', autospec=True)
def test_create_person_exists(mock_create, mock_exists):
    mock_exists.return_value = True  # Person already exists
    
    test_data = {
        ep.ppl.NAME: "Test Person",
        ep.ppl.EMAIL: "test@nyu.edu",
        ep.ppl.AFFILIATION: "NYU",
        ep.ppl.ROLES: "AU"
    }
    
    resp = TEST_CLIENT.put(f'{ep.PEOPLE_EP}/create', json=test_data)
    assert resp.status_code == NOT_ACCEPTABLE
    
    mock_exists.assert_called_once_with("test@nyu.edu")
    mock_create.assert_not_called()  # create should never be called if person exists


@patch('data.people.delete', return_value='delete@nyu.edu')
def test_delete_person_success(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/delete@nyu.edu')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'Deleted' in resp_json
    mock_delete.assert_called_once()


@patch('data.people.delete', return_value=None)
def test_delete_person_not_found(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/nonexistent@email.com')
    assert resp.status_code == NOT_FOUND


def test_get_endpoints():
    resp = TEST_CLIENT.get(ep.ENDPOINT_EP)
    resp_json = resp.get_json()
    assert "Available endpoints" in resp_json
    assert isinstance(resp_json["Available endpoints"], list)
    assert len(resp_json["Available endpoints"]) > 0


@patch('data.people.get_masthead', return_value={})
def test_get_masthead(mock_masthead):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/masthead')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.MASTHEAD in resp_json
    assert isinstance(resp_json[ep.MASTHEAD], dict)