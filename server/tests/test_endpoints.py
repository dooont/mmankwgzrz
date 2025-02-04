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
from data.manuscripts import form
from data.manuscripts import query 
from data.manuscripts import fields as flds

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()


def test_get_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_get_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    print(f'{ep.TITLE_EP=}')
    resp_json = resp.get_json()
    print(f'{resp_json=}')
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)
    assert len(resp_json[ep.TITLE_RESP]) > 0


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
    assert form_data[ep.ppl.NAME] == "string"
    assert form_data[ep.ppl.EMAIL] == "string"
    assert form_data[ep.ppl.AFFILIATION] == "string"


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


@patch('data.people.read', autospec=True)
def test_get_people_by_role(mock_read):
    mock_data = {
        'user1@email.com': {
            'name': 'User 1',
            'roles': ['AU', 'CE']
        },
        'user2@email.com': {
            'name': 'User 2',
            'roles': ['AU']
        },
        'user3@email.com': {
            'name': 'User 3',
            'roles': ['ED']
        }
    }
    mock_read.return_value = mock_data

    # Test getting AU
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/role/AU')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'people' in resp_json
    authors = resp_json['people']
    assert len(authors) == 2
    assert all('AU' in person['roles'] for person in authors)

    # Test getting CE
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/role/CE')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    copy_editors = resp_json['people']
    assert len(copy_editors) == 1 
    assert all('CE' in person['roles'] for person in copy_editors)

    # Test non-existent role
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/role/somerole')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert len(resp_json['people']) == 0 


@patch('data.people.read', autospec=True)
def test_get_people_by_affiliation(mock_read):
    mock_data = {
        'user1@email.com': {
            'name': 'User 1',
            'affiliation': 'NYU'
        },
        'user2@email.com': {
            'name': 'User 2',
            'affiliation': 'NYU'
        },
        'user3@email.com': {
            'name': 'User 3',
            'affiliation': 'BYU'
        }
    }
    mock_read.return_value = mock_data

    # Test getting NYU
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/affiliation/NYU')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'people' in resp_json
    people = resp_json['people']
    assert len(people) == 2
    assert all('NYU' in person['affiliation'] for person in people)

    # Test getting BYU
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/affiliation/BYU')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'people' in resp_json
    people = resp_json['people']
    assert len(people) == 1
    assert all('BYU' in person['affiliation'] for person in people)

    # Test non-existent affiliation
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/affiliation/a')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert len(resp_json['people']) == 0 


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


@patch('data.manuscripts.query.get_manuscripts', return_value={'id': {flds.TITLE: 'Three Bears', 
                                                    flds.AUTHOR: 'Andy Ng', flds.AUTHOR_EMAIL: 'an3299@nyu.edu', 
                                                    flds.REFEREES: ['bob898@nyu.edu'], flds.STATE: 'Submitted', 
                                                    flds.ACTION: 'Assign Ref'}})
def test_get_manuscripts(mock_read):
        resp = TEST_CLIENT.get(f'{ep.QUERY_EP}')
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert isinstance(resp_json, dict)
        for _id, manuscript in resp_json.items():
            assert isinstance(_id, str)
            assert len(_id) > 0
            assert flds.TITLE in manuscript
            assert flds.AUTHOR in manuscript
            assert flds.AUTHOR_EMAIL in manuscript
            assert flds.REFEREES in manuscript
            assert flds.STATE in manuscript
            assert flds.ACTION in manuscript

        
def test_get_form():
    with patch('data.manuscripts.form.get_form', return_value=[]) as mock_get_form:
        resp = TEST_CLIENT.get(ep.FORM_EP)
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert isinstance(resp_json, list)
        mock_get_form.assert_called_once()

def test_get_form_field():
    field_name = "test_field"
    field_data = {
        form.FLD_NM: field_name,
        'question': 'Test Question',
        'param_type': 'string',
        'optional': True
    }

    with patch('data.manuscripts.form.get_form', return_value=[field_data]) as mock_get_form:
        resp = TEST_CLIENT.get(f'{ep.FORM_EP}/{field_name}')
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert resp_json == field_data
        mock_get_form.assert_called_once()

    with patch('data.manuscripts.form.get_form', return_value=[]) as mock_get_form:
        resp = TEST_CLIENT.get(f'{ep.FORM_EP}/{field_name}')
        assert resp.status_code == NOT_FOUND
        mock_get_form.assert_called_once()


def test_create_form_field():
    new_field_data = {
        'field_name': 'new_field',
        'question': 'New Question',
        'param_type': 'string',
        'optional': True
    }

    with patch('data.manuscripts.form.get_form', return_value=[]) as mock_get_form:
        resp = TEST_CLIENT.put(f'{ep.FORM_EP}/create', json=new_field_data)
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert ep.MESSAGE in resp_json
        assert ep.RETURN in resp_json
        mock_get_form.assert_called_once()

    with patch('data.manuscripts.form.get_form', return_value=[{form.FLD_NM: 'new_field'}]) as mock_get_form:
        resp = TEST_CLIENT.put(f'{ep.FORM_EP}/create', json=new_field_data)
        assert resp.status_code == NOT_ACCEPTABLE
        mock_get_form.assert_called_once()


def test_delete_form_field():
    field_name = "test_field"
    field_data = {
        form.FLD_NM: field_name,
        'question': 'Test Question',
        'param_type': 'string',
        'optional': True
    }

    with patch('data.manuscripts.form.get_form', return_value=[field_data]) as mock_get_form:
        resp = TEST_CLIENT.delete(f'{ep.FORM_EP}/{field_name}')
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert 'Deleted' in resp_json
        mock_get_form.assert_called_once()

    with patch('data.manuscripts.form.get_form', return_value=[]) as mock_get_form:
        resp = TEST_CLIENT.delete(f'{ep.FORM_EP}/{field_name}')
        assert resp.status_code == NOT_FOUND
        mock_get_form.assert_called_once()

def test_update_form_field():
    field_name = "test_field"
    update_data = {
        'question': 'Updated Question',
        'param_type': 'integer',
        'optional': False
    }

    with patch('data.manuscripts.form.get_form', return_value=[{form.FLD_NM: field_name}]) as mock_get_form:
        resp = TEST_CLIENT.put(f'{ep.FORM_EP}/{field_name}', json=update_data)
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert ep.MESSAGE in resp_json
        assert ep.RETURN in resp_json
        mock_get_form.assert_called_once()

    with patch('data.manuscripts.form.get_form', return_value=[]) as mock_get_form:
        resp = TEST_CLIENT.put(f'{ep.FORM_EP}/{field_name}', json=update_data)
        assert resp.status_code == NOT_FOUND
        mock_get_form.assert_called_once()


@patch('data.text.create', autospec=True, return_value={"message": "Test text created"})
def test_create_text(mock_create):
    text_data = {"key": "test_key", "title": "Test Title", "text": "This is a new text message"}
    resp = TEST_CLIENT.put(f'{ep.TEXT_EP}/create', json=text_data)
    assert resp.status_code == OK
    mock_create.assert_called_once_with("test_key", "Test Title", "This is a new text message")


@patch('data.text.read_one', autospec=True, return_value={"text": "This is a new text message"})
def test_read_text(mock_read_one):
    text_id = "sample_id"
    resp = TEST_CLIENT.get(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == OK
    mock_read_one.assert_called_once_with(text_id)


@patch('data.text.read_one', autospec=True, return_value=None)
def test_read_text_not_found(mock_read_one):
    text_id = "nonexistent_id"
    resp = TEST_CLIENT.get(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == NOT_FOUND
    mock_read_one.assert_called_once_with(text_id)


@patch('data.text.update', autospec=True, return_value={"updated_text": "Updated text message"})
def test_update_text(mock_update):
    text_id = "sample_id"
    update_data = {"title": "Updated Title", "text": "Updated text message"}
    resp = TEST_CLIENT.put(f'{ep.TEXT_EP}/{text_id}', json=update_data)
    assert resp.status_code == OK
    mock_update.assert_called_once_with(text_id, title="Updated Title", text="Updated text message")


def test_update_text_invalid_data():
    text_id = "sample_id"
    invalid_data = {"title": "Updated Title", "text": ""}  # Empty text should not be allowed

    resp = TEST_CLIENT.put(f'{ep.TEXT_EP}/{text_id}', json=invalid_data)
    assert resp.status_code == NOT_ACCEPTABLE


@patch('data.text.delete', autospec=True, return_value="Text deleted")
def test_delete_text(mock_delete):
    text_id = "sample_id"
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == OK
    mock_delete.assert_called_once_with(text_id)


@patch('data.text.delete', autospec=True, side_effect=ValueError("No text entry found for key 'nonexistent_id'"))
def test_delete_text_not_found(mock_delete):
    text_id = "nonexistent_id"
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == NOT_FOUND
    mock_delete.assert_called_once_with(text_id)

