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

TEST_PERSON_DICT = {
    TEST_EMAIL: {
        NAME: 'Eugene Callahan',
        ROLES: [],
        AFFILIATION: 'NYU',
        EMAIL: TEST_EMAIL
    }
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
