import pytest
import data.people as ppl
from data.roles import TEST_CODE

NO_AT = 'jkajsd'
NO_NAME = '@kalsj'
NO_DOMAIN = 'kajshd@'
NO_SUB_DOMAIN = 'kajshd@com'
DOMAIN_TOO_SHORT = 'kajshd@nyu.e'
DOMAIN_TOO_LONG = 'kajshd@nyu.eedduu'

TEMP_EMAIL = 'temp_person@temp.org'

@pytest.fixture(scope='function')
def temp_person():
    ret = ppl.create('Joe Smith', 'NYU', TEMP_EMAIL, TEST_CODE)
    yield ret
    ppl.delete(ret)

#testing the read endpoint
def test_read():
    people = ppl.read()
    assert isinstance(people, dict)
    assert len(people) > 0
    # Check for string IDs:
    for _id, person in people.items():
        # id represents the key and person represents
        # the value of each dict item
        # people.items() returns a list of dictionary key-val pairs
        assert isinstance(_id, str)
        # checks if NAME is a key in the person (value)
        assert ppl.NAME in person


def test_read_one(temp_person):
    assert ppl.read_one(temp_person) is not None


def test_read_one_not_there():
    assert ppl.read_one('Not an existing email!') is None

# testing the delete endpoint
def test_delete():
    people = ppl.read()
    assert isinstance(people, dict)
    old_len = len(people)
    ppl.delete(ppl.DEL_EMAIL)
    people = ppl.read()
    # checks if new people dict has length smaller than old
    assert len(people) < old_len
    # make sure the email deleted is still not in people dict
    assert ppl.DEL_EMAIL not in people


# email is made constant here to make it easier to change later on
ADD_EMAIL = 'joe@nyu.edu'


# testing the create endpoint
def test_create():
    # creates the person
    ppl.create('Joe Smith', 'NYU', ADD_EMAIL, TEST_CODE)
    people = ppl.read()
    # checks if ADD_EMAIL is in people already
    assert ADD_EMAIL in people


# testing the delete people endpoint
def test_create_duplicate():
    # checks if the email already exists after creating the person
    # if so, it will raise an error
    with pytest.raises(ValueError):
        ppl.create('Name Does Not matter',
                   'Neither Does School', ppl.TEST_EMAIL, TEST_CODE)


# testing the update endpoint
def test_update():
    test_email = "test@nyu.edu"
    ppl.create('name', 'NYU', test_email, TEST_CODE)

    new_name = "updated name"
    result = ppl.update(test_email, name=new_name)

    assert result == test_email
    people = ppl.read()
    assert people[test_email][ppl.NAME] == new_name

    assert ppl.update("nonexistent@nyu.edu", name="Test") is None

    with pytest.raises(ValueError):
        ppl.update(test_email, role="invalid_role")


VALID_ROLES = ['ED', 'AU']


@pytest.mark.skip('Skipping cause not done.')
def test_update(temp_person):
    ppl.update('Buffalo Bill', 'UBuffalo', temp_person, VALID_ROLES)


# Some constants to test email validation
VALID_EMAIL = 'example@gmail.com'
NO_AT = 'example'
NO_NAME = '@gmail.com'
NO_DOMAIN = 'example@'
NO_TLD = 'example@gmail'


# Tests for the email validation
def test_is_valid_email():
    assert ppl.is_valid_email(VALID_EMAIL)


def test_is_valid_email_no_at():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_AT)


# Tests that there exists a name
def test_is_valid_no_name():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_NAME)


# Test that there exists a domain
def test_is_valid_no_domain():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_DOMAIN)


# Tests that there exists a top level domain
def test_is_valid_no_tld():
    with pytest.raises(ValueError):
        ppl.is_valid_email(NO_TLD)


# Test that checks how bad emails are handled
def test_create_bad_email():
    with pytest.raises(ValueError):
        ppl.create('Do not care about name',
                   'Or affiliation', 'bademail', TEST_CODE)
        

def test_get_masthead():
    mh = ppl.get_masthead()
    assert isinstance(mh, dict)