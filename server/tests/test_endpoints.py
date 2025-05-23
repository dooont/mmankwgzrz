from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
    UNAUTHORIZED,
)

from unittest.mock import patch

import pytest

from data.people import NAME
from data.manuscripts import form
import data.manuscripts.form_filler as ff
from data.manuscripts import query 
from data.manuscripts import fields as flds

import security.security as sec

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


@patch('security.security.is_permitted', return_value=True)
def test_permissions_granted(mock_permitted):
    resp = TEST_CLIENT.get('/permissions?feature=text&action=update&user_email=editor@nyu.edu')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert "permitted" in resp_json
    assert resp_json["permitted"] is True
    mock_permitted.assert_called_once_with("text", "update", "editor@nyu.edu")


@patch('security.security.is_permitted', return_value=False)
def test_permissions_denied(mock_permitted):
    resp = TEST_CLIENT.get('/permissions?feature=text&action=update&user_email=author@nyu.edu')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert "permitted" in resp_json
    assert resp_json["permitted"] is False
    mock_permitted.assert_called_once_with("text", "update", "author@nyu.edu")


def test_permissions_missing_params():
    resp = TEST_CLIENT.get('/permissions')
    assert resp.status_code == BAD_REQUEST


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
    assert ep.ppl.ROLES in form_data
    assert form_data[ep.ppl.NAME] == 'string'
    assert form_data[ep.ppl.EMAIL] == 'string'
    assert form_data[ep.ppl.AFFILIATION] == 'string'
    assert form_data[ep.ppl.ROLES] == 'list of strings'


@patch('data.people.exists', autospec=True)
@patch('data.people.create', autospec=True, return_value='test@nyu.edu')
def test_create_person(mock_create, mock_exists):
    mock_exists.return_value = False  # assume person doesn't exist yet
    
    test_data = {
        ep.ppl.NAME: 'Test Person',
        ep.ppl.EMAIL: mock_create.return_value,
        ep.ppl.AFFILIATION: 'NYU',
        ep.ppl.ROLES: 'AU',
    }
    
    resp = TEST_CLIENT.put(f'{ep.PEOPLE_EP}/create', json=test_data)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json
    assert resp_json[ep.RETURN] == 'test@nyu.edu'
    assert resp_json[ep.MESSAGE] == 'Person added!'
    assert resp_json[ep.RETURN] == mock_create.return_value
    
    mock_exists.assert_called_once_with('test@nyu.edu')
    mock_create.assert_called_once()


@patch('data.people.exists', autospec=True)
@patch('data.people.create', autospec=True)
def test_create_person_exists(mock_create, mock_exists):
    mock_exists.return_value = True  # Person already exists
    
    test_data = {
        ep.ppl.NAME: 'Test Person',
        ep.ppl.EMAIL: 'test@nyu.edu',
        ep.ppl.AFFILIATION: 'NYU',
        ep.ppl.ROLES: 'AU',
    }
    # UP TO HERE !!!
    resp = TEST_CLIENT.put(f'{ep.PEOPLE_EP}/create', json=test_data)
    assert resp.status_code == NOT_ACCEPTABLE
    
    mock_exists.assert_called_once_with('test@nyu.edu')
    mock_create.assert_not_called()  # create should never be called if person exists


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
    assert 'Available endpoints' in resp_json
    assert isinstance(resp_json['Available endpoints'], list)
    assert len(resp_json['Available endpoints']) > 0


@patch('data.people.get_masthead', return_value={})
def test_get_masthead(mock_masthead):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/masthead')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert ep.MASTHEAD in resp_json
    assert isinstance(resp_json[ep.MASTHEAD], dict)


@patch('data.manuscripts.query.get_active_manuscripts')
@patch('data.people.exists')
def test_get_active_manuscripts_endpoint(mock_exists, mock_get_active):
    test_email = 'user@example.com'
    dummy_response = [{
        flds.ID: '123',
        flds.TITLE: 'Sample Manuscript',
        flds.AUTHOR: 'Author Name',
        flds.AUTHOR_EMAIL: test_email,
        flds.REFEREES: [],
        flds.STATE: 'SUB',
        flds.TEXT: 'Some text',
        flds.ABSTRACT: 'Some abstract'
    }]
    
    mock_exists.return_value = True
    mock_get_active.return_value = dummy_response

    response = TEST_CLIENT.get(f'{ep.QUERY_EP}/active/{test_email}')
    assert response.status_code == 200
    assert response.get_json() == dummy_response


@patch('data.manuscripts.query.get_manuscripts', return_value={'id': {flds.TITLE: 'Three Bears', 
                                                    flds.AUTHOR: 'Andy Ng', flds.AUTHOR_EMAIL: 'an3299@nyu.edu',
                                                    flds.REFEREES: ['bob898@nyu.edu'], flds.STATE: 'Submitted',
                                                    flds.TEXT: 'Text', flds.ABSTRACT: 'Abstract'}})
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
            assert flds.TEXT in manuscript
            assert flds.ABSTRACT in manuscript
            # assert flds.ACTION in manuscript


@patch('data.manuscripts.query.exists')
@patch('data.manuscripts.query.create_manuscript')
def test_create_manuscript(mock_create, mock_exists):
    mock_exists.return_value = False
    mock_create.return_value = '1'
    
    test_data = {
        flds.TITLE: 'Test Manuscript',
        flds.AUTHOR: 'Test Author',
        flds.AUTHOR_EMAIL: 'test@nyu.com',
        flds.REFEREES: [],
        flds.STATE: 'SUB',
        flds.TEXT: 'Text',
        flds.ABSTRACT: 'Abstract',
    }
    
    resp = TEST_CLIENT.put(f'{ep.QUERY_EP}/create', json=test_data)
    resp_json = resp.get_json()

    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json
    assert resp_json[ep.RETURN] == '1'


@patch('data.manuscripts.query.exists')
@patch('data.manuscripts.query.update')
def test_update_manuscript(mock_update, mock_exists):
    mock_exists.return_value = True  
    mock_update.return_value = '1'  

    test_data = {
        flds.ID: '1',
        flds.TITLE: 'Updated Test Manuscript',
        flds.AUTHOR: 'Test Author',
        flds.AUTHOR_EMAIL: 'test@nyu.com',
        flds.REFEREES: [],
        flds.STATE: 'SUB',
        flds.TEXT: 'Text',
        flds.ABSTRACT: 'Abstract',
    }

    response = TEST_CLIENT.put(f'{ep.QUERY_EP}/1', json=test_data)
    response_json = response.get_json()

    assert ep.MESSAGE in response_json
    assert response_json[ep.MESSAGE] == 'Manuscript updated successfully'
    assert ep.RETURN in response_json
    assert response_json[ep.RETURN] == '1'


@patch('data.manuscripts.query.get_one_manu')
def test_get_one_manuscript(mock_get_one):
    mock_get_one.return_value = {
        flds.ID: '1',
        flds.TITLE: 'Test Manuscript',
        flds.AUTHOR: 'Test Author',
        flds.AUTHOR_EMAIL: 'test@nyu.com',
        flds.REFEREES: [],
        flds.STATE: 'SUB',
        flds.TEXT: 'Text',
        flds.ABSTRACT: 'Abstract',
    }

    response = TEST_CLIENT.get(f'{ep.QUERY_EP}/1')
    response_json = response.get_json()

    assert response_json[flds.ID] == '1'
    assert response_json[flds.TITLE] == 'Test Manuscript'
    assert response_json[flds.AUTHOR] == 'Test Author'
    assert response_json[flds.AUTHOR_EMAIL] == 'test@nyu.com'
    assert response_json[flds.STATE] == 'SUB'
    assert response_json[flds.TEXT] =='Text'
    assert response_json[flds.ABSTRACT] == 'Abstract'


@patch('data.manuscripts.query.delete')
def test_delete_manuscript(mock_delete):
    mock_delete.return_value = 1  

    response = TEST_CLIENT.delete(f'{ep.QUERY_EP}/1')
    response_json = response.get_json()

    assert response_json['Deleted'] == 1

        
def test_get_form():
    with patch('data.manuscripts.form.get_form', return_value=[]) as mock_get_form:
        resp = TEST_CLIENT.get(ep.FORM_EP)
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert isinstance(resp_json, list)
        mock_get_form.assert_called_once()


def test_get_form_field():
    field_name = 'test_field'
    field_data = {
        ff.FLD_NM: field_name,
        ff.QSTN: 'Test Question',
        ff.PARAM_TYPE: 'string',
        ff.OPT: True
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
        ff.FLD_NM: 'new_field',
        ff.QSTN: 'New Question',
        ff.PARAM_TYPE: 'string',
        ff.OPT: True
    }

    with patch('data.manuscripts.form.get_form', return_value=[]) as mock_get_form:
        resp = TEST_CLIENT.put(f'{ep.FORM_EP}/create', json=new_field_data)
        assert resp.status_code == OK
        resp_json = resp.get_json()
        assert ep.MESSAGE in resp_json
        assert ep.RETURN in resp_json
        mock_get_form.assert_called_once()

    with patch('data.manuscripts.form.get_form', return_value=[{ff.FLD_NM: 'new_field'}]) as mock_get_form:
        resp = TEST_CLIENT.put(f'{ep.FORM_EP}/create', json=new_field_data)
        assert resp.status_code == NOT_ACCEPTABLE
        mock_get_form.assert_called_once()


def test_delete_form_field():
    field_name = 'test_field'
    field_data = {
        ff.FLD_NM: field_name,
        ff.QSTN: 'Test Question',
        ff.PARAM_TYPE: 'string',
        ff.OPT: True
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
    field_name = 'test_field'
    update_data = {
        ff.QSTN: 'Updated Question',
        ff.PARAM_TYPE: 'integer',
        ff.OPT: False
    }

    with patch('data.manuscripts.form.get_form', return_value=[{ff.FLD_NM: field_name}]) as mock_get_form:
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


@patch('data.text.create', autospec=True, return_value={'message': 'Test text created'})
def test_create_text(mock_create):
    text_data = {'key': 'test_key', 'title': 'Test Title', 'text': 'This is a new text message'}
    resp = TEST_CLIENT.put(f'{ep.TEXT_EP}/create', json=text_data)
    assert resp.status_code == OK
    mock_create.assert_called_once_with('test_key', 'Test Title', 'This is a new text message')


@patch('data.text.read_one', autospec=True, return_value={'text': 'This is a new text message'})
def test_read_text(mock_read_one):
    text_id = 'sample_id'
    resp = TEST_CLIENT.get(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == OK
    mock_read_one.assert_called_once_with(text_id)


@patch('data.text.read_one', autospec=True, return_value=None)
def test_read_text_not_found(mock_read_one):
    text_id = 'nonexistent_id'
    resp = TEST_CLIENT.get(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == NOT_FOUND
    mock_read_one.assert_called_once_with(text_id)


@patch('data.text.update', autospec=True, return_value={'updated_text': 'Updated text message'})
def test_update_text(mock_update):
    text_id = 'sample_id'
    update_data = {'title': 'Updated Title', 'text': 'Updated text message'}
    resp = TEST_CLIENT.put(f'{ep.TEXT_EP}/{text_id}', json=update_data)
    assert resp.status_code == OK
    mock_update.assert_called_once_with(text_id, title='Updated Title', text='Updated text message')


def test_update_text_invalid_data():
    text_id = 'sample_id'
    invalid_data = {'title': 'Updated Title', 'text': ''}  # Empty text should not be allowed

    resp = TEST_CLIENT.put(f'{ep.TEXT_EP}/{text_id}', json=invalid_data)
    assert resp.status_code == NOT_ACCEPTABLE


@patch('data.text.delete', autospec=True, return_value='Text deleted')
def test_delete_text(mock_delete):
    text_id = 'sample_id'
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == OK
    mock_delete.assert_called_once_with(text_id)


@patch('data.text.delete', autospec=True, side_effect=ValueError("No text entry found for key 'nonexistent_id'"))
def test_delete_text_not_found(mock_delete):
    text_id = 'nonexistent_id'
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/{text_id}')
    assert resp.status_code == NOT_FOUND
    mock_delete.assert_called_once_with(text_id)


def test_get_states():
    resp = TEST_CLIENT.get(f'{ep.QUERY_EP}/states')
    resp_json = resp.get_json()
    assert query.AUTHOR_REVIEW in resp_json


def test_get_actions():
    resp = TEST_CLIENT.get(f'{ep.QUERY_EP}/actions')
    resp_json = resp.get_json()
    assert 'ACC' in resp_json
    assert 'WDN' in resp_json


@patch('data.people.read_one')
@patch('data.manuscripts.query.get_one_manu')
def test_get_valid_actions(mock_get_manu, mock_read_one):
    mock_read_one.return_value = {
        "email": "referee@nyu.com",
        "roles": ["RE"]
    }

    mock_get_manu.return_value = {
        "author_email": "test1234@nyu.com",
        "state": query.REFEREE_REVIEW,
        "referees": ["referee@nyu.com"]
    }

    resp = TEST_CLIENT.get(
        f"{ep.QUERY_EP}/actions?user_email=referee@nyu.com&manu_id=fake123"
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()

    assert "SBR" in resp_json


@patch('data.account.login', side_effect=ValueError("Invalid credentials"))
def test_login_fail(mock_login):
    invalid_data = {ep.acc.EMAIL: '', ep.acc.PASSWORD: ''}
    resp = TEST_CLIENT.post(f'{ep.LOGIN_EP}', json=invalid_data)
    assert resp.status_code == BAD_REQUEST

    # email is nonempty but password is still empty
    invalid_data[ep.acc.EMAIL] = 'email@nyu.edu'
    resp = TEST_CLIENT.post(f'{ep.LOGIN_EP}', json=invalid_data)
    assert resp.status_code == BAD_REQUEST

    # both are nonempty, but some error was thrown
    invalid_data[ep.acc.PASSWORD] = 'password'
    resp = TEST_CLIENT.post(f'{ep.LOGIN_EP}', json=invalid_data)
    assert resp.status_code == BAD_REQUEST


@patch('data.account.login', return_value=True)
def test_login_success(mock_login):
    valid_data = {ep.acc.EMAIL: 'email@nyu.edu', ep.acc.PASSWORD: 'password'}
    resp = TEST_CLIENT.post(f'{ep.LOGIN_EP}', json=valid_data)
    assert resp.status_code == OK


@patch('data.account.register', side_effect=ValueError("Invalid credentials"))
def test_register_fail(mock_register):
    invalid_data = {ep.acc.EMAIL: '', ep.acc.PASSWORD: ''}
    resp = TEST_CLIENT.post(f'{ep.REGISTER_EP}', json=invalid_data)
    assert resp.status_code == BAD_REQUEST

    # email is valid but password is still empty
    invalid_data[ep.acc.EMAIL] = 'email@nyu.edu'
    resp = TEST_CLIENT.post(f'{ep.REGISTER_EP}', json=invalid_data)
    assert resp.status_code == BAD_REQUEST

    # both are nonempty, but some error was thrown
    invalid_data[ep.acc.PASSWORD] = 'password'
    resp = TEST_CLIENT.post(f'{ep.REGISTER_EP}', json=invalid_data)
    assert resp.status_code == BAD_REQUEST


@patch('data.account.register', return_value='email@nyu.edu')
def test_register_success(mock_register):
    valid_data = {ep.acc.EMAIL: 'email@nyu.edu', ep.acc.PASSWORD: 'password'}
    resp = TEST_CLIENT.post(f'{ep.REGISTER_EP}', json=valid_data)
    assert resp.status_code == OK


@patch('data.people.read_one', return_value={'roles': ['ED']})
@patch('data.people.delete', return_value=1)
def test_person_delete_success(mock_delete, mock_read_one):
    # email matches bearer header
    email = 'email@nyu.edu'
    headers = {
        'Authorization': f'Bearer {email}'
    }
    resp = TEST_CLIENT.delete(
        f'{ep.PEOPLE_EP}/{email}', headers=headers
    )
    assert resp.status_code == OK

    # an editor should succeed
    headers['Authorization'] = 'Bearer editor@nyu.edu'
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/{email}', headers=headers)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert 'Deleted' in resp_json
    assert type(resp_json['Deleted'] == int)


@patch('data.people.read_one', return_value={'roles': []})
@patch('data.people.delete')
def test_person_delete_unauthorized(mock_delete, mock_read_one):
    target_email = 'someoneelse@nyu.edu'
    bearer_email = 'unauthorized@nyu.edu'
    headers = {
        'Authorization': f'Bearer {bearer_email}'
    }
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/{target_email}', headers=headers)

    assert resp.status_code == UNAUTHORIZED


# TODO: fix test. add bearer field
def test_update_person():
    test_email = 'ejc369@nyu.edu'
    bearer_email = 'ejc369@nyu.edu'
    update_data = {
        ep.ppl.NAME: 'Updated Name',
        ep.ppl.AFFILIATION: 'New Affiliation',
        ep.ppl.ROLES: ['AU', 'CE'],
    }
    headers = {
        'Authorization': f'Bearer {bearer_email}'
        }

    # Success case
    with patch('data.people.read_one', autospec=True) as mock_read_one, \
         patch('data.people.update', autospec=True, return_value=update_data) as mock_update:
        # Mock that person exists
        mock_read_one.return_value = {'email': test_email}  
        
        
        resp = TEST_CLIENT.put(
            f'{ep.PEOPLE_EP}/{test_email}',
            json=update_data,
            headers=headers
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
            json=update_data,
            headers=headers
        )
        assert resp.status_code == NOT_FOUND

    # # Invalid data case
    with patch('data.people.read_one') as mock_read_one:
        mock_read_one.return_value = {'email': test_email}  
        invalid_data = {
            ep.ppl.NAME: '',  # invalid empty name
            ep.ppl.AFFILIATION: '',
            ep.ppl.ROLES: ['nonexistent_role'],  # invalid role
        }
        resp = TEST_CLIENT.put(
            f'{ep.PEOPLE_EP}/{test_email}',
            json=invalid_data,
            headers=headers
        )
        assert resp.status_code == NOT_ACCEPTABLE


@patch('data.people.read_one', return_value={'roles': []})
@patch('data.people.delete', return_value=0)
def test_account_delete_unauthorized(mock_delete, mock_read_one):
    email = 'email@nyu.edu'
    headers = {
        'Authorization': f'Bearer unauthorized@nyu.edu'
    }
    resp = TEST_CLIENT.delete(f'{ep.ACCOUNT_EP}/{email}', headers=headers)
    assert resp.status_code == UNAUTHORIZED


@patch('data.account.delete', return_value=True)
@patch('data.people.delete', return_value=1)
def test_account_delete_success(mock_account_delete, mock_people_delete):
    email = 'email@nyu.edu'
    headers = {
        'Authorization': f'Bearer {email}'
    }
    resp = TEST_CLIENT.delete(f'{ep.ACCOUNT_EP}/{email}', headers=headers)
    assert resp.status_code == OK


@patch('data.account.delete', side_effect=ValueError("Account does not exist"))
@patch('data.people.delete', return_value=0)
def test_account_delete_fail(mock_account_delete, mock_people_delete):
    email = 'nonexistent@nyu.edu'
    headers = {
        'Authorization': f'Bearer {email}'
    }
    resp = TEST_CLIENT.delete(f'{ep.ACCOUNT_EP}/{email}', headers=headers)
    assert resp.status_code == BAD_REQUEST


@patch('data.manuscripts.query.can_choose_action', return_value=True)
def test_can_choose_action_endpoint_true(mock_check):
    resp = TEST_CLIENT.get('/query/can_choose_action', query_string={
        'manu_id': 'mock123',
        'user_email': 'editor@nyu.edu'
    })
    assert resp.status_code == OK
    assert resp.get_json() is True
    mock_check.assert_called_once_with('mock123', 'editor@nyu.edu')


@patch('data.manuscripts.query.can_choose_action', side_effect=Exception("Boom"))
def test_can_choose_action_endpoint_error(mock_check):
    resp = TEST_CLIENT.get('/query/can_choose_action', query_string={
        'manu_id': 'mock123',
        'user_email': 'editor@nyu.edu'
    })
    assert resp.status_code == BAD_REQUEST
    assert "Error checking action permissions" in resp.get_data(as_text=True)


def test_can_choose_action_endpoint_missing_param():
    resp = TEST_CLIENT.get('/query/can_choose_action', query_string={
        'user_email': 'editor@nyu.edu'
    })
    assert resp.status_code == BAD_REQUEST


@patch('data.manuscripts.query.can_move_action', return_value = True)
def test_can_move_action_endpoint_true(mock_check):
    resp = TEST_CLIENT.get('/query/can_move_action', query_string={
        'manu_id': 'mock123',
        'user_email': 'editor@nyu.edu'
    })
    assert resp.status_code == OK
    assert resp.get_json() is True


@patch('data.manuscripts.query.get_valid_actions', return_value=['ACC', 'REJ'])
def test_valid_actions_endpoint_success(mock_actions):
    resp = TEST_CLIENT.get('/query/valid_actions', query_string={
        'manu_id': 'mock321',
        'user_email': 'ed@nyu.edu'
    })
    assert resp.status_code == OK
    assert resp.get_json() == ['ACC', 'REJ']
    mock_actions.assert_called_once_with('mock321', 'ed@nyu.edu')


@patch('data.manuscripts.query.get_valid_actions', side_effect=ValueError("Invalid"))
def test_valid_actions_endpoint_value_error(mock_actions):
    resp = TEST_CLIENT.get('/query/valid_actions', query_string={
        'manu_id': 'bad-id',
        'user_email': 'user@nyu.edu'
    })
    assert resp.status_code == BAD_REQUEST
    assert "Invalid" in resp.get_data(as_text=True)


def test_valid_actions_endpoint_missing_param():
    resp = TEST_CLIENT.get('/query/valid_actions', query_string={
        'user_email': 'someone@nyu.edu'
    })
    assert resp.status_code == BAD_REQUEST


@patch('data.manuscripts.query.get_valid_states', return_value=['AU_RVW', 'SUB'])
def test_valid_states_endpoint_success(mock_states):
    resp = TEST_CLIENT.get('/query/valid_states', query_string={
        'manu_id': 'test123',
        'user_email': 'test@nyu.edu'
    })
    assert resp.status_code == OK
    assert resp.get_json() == ['AU_RVW', 'SUB']
    mock_states.assert_called_once_with('test123', 'test@nyu.edu')
