import data.people as ppl


def test_get_people():
    people = ppl.get_people()
    assert isinstance(people, dict)
    assert len(people) > 0
    # Check for string IDs:
    for _id in people:
        assert isinstance(_id, str)
    