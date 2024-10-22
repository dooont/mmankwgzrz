import pytest
import data.people as ppl

from data.roles import TEST_CODE

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
