"""
This module interfaces to our user data.
"""

MIN_USER_NAME_LEN = 2
# Fields
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'

TEST_EMAIL = 'ejc369@nyu.edu'
DEL_EMAIL = 'delete@nyu.edu'


TEST_PERSON_DICT = {
    TEST_EMAIL: {
        NAME: 'Eugene Callahan',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: TEST_EMAIL
    },
    DEL_EMAIL: {
        NAME: 'Another Person',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: DEL_EMAIL,
    },
}


def get_people():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each email must be the key for another dictionary.
    """
    people = TEST_PERSON_DICT
    return people


def delete_person(_id):
    people = get_people()
    if _id in people:
        del people[_id]
        return _id
    else:
        return None


def create_person(name: str, affiliation: str, email: str):
    if email in TEST_PERSON_DICT:
        raise ValueError('Email: {email=} already exists')
    TEST_PERSON_DICT[email] = {
      NAME: name, AFFILIATION: affiliation, EMAIL: email
    }
