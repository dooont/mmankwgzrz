import pytest

import data.people as ppl
from data.roles import TEST_CODE as TEST_ROLE_CODE

NO_AT = 'example'
NO_NAME = '@nyu'
NO_DOMAIN = 'example@'
NO_SUB_DOMAIN = 'example@com'
DOMAIN_TOO_SHORT = 'example@nyu.e'
TEMP_EMAIL = 'temp_person@temp.org'
ADD_EMAIL = 'joe@nyu.edu'
VALID_ROLES = ['ED', 'AU']


def test_is_valid_email():
    assert ppl.is_valid_email('example@nyu.edu')


def test_is_valid_email_no_at():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_AT)


def test_is_valid_no_name():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_NAME)


def test_is_valid_no_domain():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_DOMAIN)


def test_is_valid_no_sub_domain():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_SUB_DOMAIN)


def test_is_valid_email_domain_too_short():
    with pytest.raises(ValueError):
        ppl.is_valid_email(DOMAIN_TOO_SHORT)


def test_create_bad_email():
    with pytest.raises(ValueError):
        ppl.create('Do not care about name',
                   'Or affiliation', 'bademail', [TEST_ROLE_CODE])


@pytest.fixture(scope='function')
def temp_person():
    email = ppl.create('Joe Smith', 'NYU', TEMP_EMAIL, [TEST_ROLE_CODE]) 
    # yields return email as a sample or instance for testing 
    yield email 
    try:
        ppl.delete(email)
    except:
        print('Person already deleted.')


def test_read(temp_person):
    # people eturns a dictionary of dictionaries with the specified key
    people = ppl.read()
    assert isinstance(people, dict)
    assert len(people) > 0

    for _id, person in people.items():
        assert isinstance(_id, str)
        # person is a regular person dictionary
        assert ppl.NAME in person
    assert temp_person in people


def test_read_one(temp_person):
    assert ppl.read_one(temp_person) is not None


def test_read_one_not_found():
    assert ppl.read_one('Not an existing email!') is None


def test_exists(temp_person):
    assert ppl.exists(temp_person)


def test_doesnt_exist():
    assert not ppl.exists('Not an existing email!')


def test_delete(temp_person):
    ppl.delete(temp_person)
    assert not ppl.exists(temp_person)


def test_create(temp_person):
    # ppl.create('Joe Smith', 'NYU', ADD_EMAIL, [TEST_ROLE_CODE])
    assert ppl.exists(temp_person)
    assert isinstance(ppl.read_one(temp_person), dict)
    assert isinstance(ppl.read_one(temp_person)[ppl.ROLES], list)
    assert isinstance(ppl.read_one(temp_person)[ppl.AFFILIATION], str)
    assert isinstance(ppl.read_one(temp_person)[ppl.NAME], str)
    assert isinstance(ppl.read_one(temp_person)[ppl.EMAIL], str)
    # ppl.delete(ADD_EMAIL)


def test_create_duplicate(temp_person):
    with pytest.raises(ValueError):
        ppl.create('Name Does Not matter',
                   'Neither Does School', temp_person, [TEST_ROLE_CODE])


def test_update(temp_person):
    new_name = 'Buffalo Bill'
    new_affiliation = 'UBuffalo'
    new_roles = VALID_ROLES

    updated_email = ppl.update(new_name, new_affiliation, temp_person, new_roles)
    assert updated_email == temp_person

    updated_person = ppl.read_one(temp_person)
    assert updated_person[ppl.NAME] == new_name
    assert updated_person[ppl.AFFILIATION] == new_affiliation
    assert updated_person[ppl.ROLES] == new_roles


def test_update_not_there():
    with pytest.raises(ValueError):
        ppl.update('Will Fail', 'University of the Void',
                   'Non-existent email', VALID_ROLES)


def test_get_masthead():
    mh = ppl.get_masthead()
    assert isinstance(mh, dict)


def test_has_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert ppl.has_role(person_rec, TEST_ROLE_CODE)


def test_doesnt_have_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert not ppl.has_role(person_rec, 'Not a good role!')


def test_create_mh_rec(temp_person):
    person_rec = ppl.read_one(temp_person)
    mh_rec = ppl.create_mh_rec(person_rec)
    assert isinstance(mh_rec, dict)
    for field in ppl.MH_FIELDS:
        assert field in mh_rec


def test_get_mh_fields():
    flds = ppl.get_mh_fields()
    assert isinstance(flds, list)
    assert len(flds) > 0


def test_delete_role(temp_person):
    ppl.delete_role(temp_person, TEST_ROLE_CODE)
    person_rec = ppl.read_one(temp_person)
    assert TEST_ROLE_CODE not in person_rec[ppl.ROLES]


def test_is_valid_person():
    assert ppl.is_valid_person(
        'test name',
        'test affiliation',
        'test@example.com',
        [TEST_ROLE_CODE],
    )


def test_not_is_valid_person():
    with pytest.raises(ValueError):
        ppl.is_valid_person(
            'test name',
            'test affiliation',
            "bad email",
            [TEST_ROLE_CODE],
        )
    with pytest.raises(Exception):
        ppl.is_valid_person(
            'test name',
            'test affiliation',
            'test@example.com',
            ['BAD CODE'],
        )
