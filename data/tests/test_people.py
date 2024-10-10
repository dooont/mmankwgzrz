import pytest
import data.people as ppl


def test_get_people():
    people = ppl.get_people()
    assert isinstance(people, dict)
    assert len(people) > 0
    # Check for string IDs:
    for _id, person in people.items():
        # id represents the key and person represents the value of each dict item
        #people.items() returns a list of dictionary key-val pairs
        assert isinstance(_id, str)
        # checks if NAME is a key in the person (value)
        assert ppl.NAME in person
    
    
def test_delete_people():
    people = ppl.get_people()
    assert isinstance(people, dict)
    old_len = len(people)
    ppl.delete_person(ppl.DEL_EMAIL)
    people = ppl.get_people()
    # checks if new people dict has length smaller than old
    assert len(people) < old_len 
    # make sure the email deleted is still not in people dict
    assert ppl.DEL_EMAIL not in people


ADD_EMAIL = 'joe@nyu.edu'

#testing the create endpoint
def test_create_person():
    ppl.create_person('Joe Smith', 'NYU', ADD_EMAIL)
    people = ppl.get_people()
    assert ADD_EMAIL in people

#testing the delete people endpoint
def test_create_duplicate():
    with pytest.raises(ValueError):
        ppl.create_person('Name Does Not matter', 'Neither Does School', ppl.TEST_EMAIL)