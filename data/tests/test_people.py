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
    