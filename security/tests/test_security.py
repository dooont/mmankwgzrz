import pytest

import security as sec
import data.people as ppl

EDITOR_EMAIL = 'temp_editor@nyu.edu'
AUTHOR_EMAIL = 'temp_author@nyu.edu'
MISSING_EMAIL = 'temp_missing@nyu.edu'

EDITOR_ROLE = 'ED'
AUTHOR_ROLE = 'AU'


@pytest.fixture(scope='function')
def temp_editor():
    email = ppl.create('Test Editor', 'NYU', EDITOR_EMAIL, [EDITOR_ROLE])
    yield email 
    try:
        ppl.delete(email)
    except:
        print('Person already deleted.')


@pytest.fixture(scope='function')
def temp_author():
    email = ppl.create('Test Author', 'NYU', AUTHOR_EMAIL, [AUTHOR_ROLE])
    yield email 
    try:
        ppl.delete(email)
    except:
        print('Person already deleted.')


def test_editor_can_update_text(temp_editor):
    assert sec.is_permitted(sec.TEXT, sec.UPDATE, temp_editor)


def test_non_editor_cannot_update_text(temp_author):
    assert not sec.is_permitted(sec.TEXT, sec.UPDATE, temp_author)


def test_missing_user():
    assert not sec.is_permitted(sec.TEXT, sec.UPDATE, MISSING_EMAIL)


def test_unprotected_feature(temp_editor):
    assert not sec.is_permitted('unprotected_feature', sec.UPDATE, temp_editor)


def test_unprotected_action(temp_editor):
    assert not sec.is_permitted(sec.TEXT, sec.READ, temp_editor)
