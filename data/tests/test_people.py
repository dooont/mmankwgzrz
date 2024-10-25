import pytest
import data.people as ppl
from data.roles import TEST_CODE


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


# testing the delete people endpoint
def test_create_duplicate():
    # checks if the email already exists after creating the person
    # if so, it will raise an error
    with pytest.raises(ValueError):
        ppl.create('Name Does Not matter',
                   'Neither Does School', ppl.TEST_EMAIL, TEST_CODE)


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