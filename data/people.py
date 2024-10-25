"""
This module interfaces to our user data.
"""
# importing python re module to match email strings based on patterns
import re
import data.roles as rls

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


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each email must be the key for another dictionary.
    """
    people = TEST_PERSON_DICT
    return people


def delete(_id):
    people = read()
    if _id in people:
        del people[_id]
        return _id
    else:
        return None


def is_valid_email(email):
    if isinstance(email, str):
        # email_format = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        email_format = '^[a-zA-Z0-9]+([_.-][a-zA-Z0-9]+)*@[a-zA-Z0-9]+([.-] \
        [a-zA-Z0-9]+)*\\.[a-zA-Z]{2,}$'
        if re.match(email_format, email):
            return True
        else:
            raise ValueError('Email does not follow correct format')
    else:
        raise ValueError('Email is not a string')


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str) -> bool:
    if email in TEST_PERSON_DICT:
        raise ValueError('Email: {email=} already exists. Adding duplicate\
                          email')
    if not is_valid_email(email):
        raise ValueError('Invalid Email: {email}')
    if not rls.is_valid(role):
        raise ValueError('Invalid Role: {role}')
    return True


def create(name: str, affiliation: str, email: str, role: str):
    if is_valid_person(name, affiliation, email, role):
        TEST_PERSON_DICT[email] = {NAME: name, ROLES: role,
                                   AFFILIATION: affiliation, EMAIL: email}
        return email


def update(email: str, name: str = None, affiliation: str = None,
           role: str = None):
    people = read()
    if email not in people:
        return None

    if name:
        people[email][NAME] = name
    if affiliation:
        people[email][AFFILIATION] = affiliation
    if role:
        if not rls.is_valid(role):
            raise ValueError(f'Invalid Role: {role}')
        people[email][ROLES] = role

    return email


def get_masthead() -> dict:
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for mh_role, text in mh_roles.items():
        people_w_role = {}
        for person in read():
            pass
            # If has_role(person):
            # Put their record in people_w_role
        masthead[text] = people_w_role
    return masthead


def main():
    print(read())


if __name__ == '__main__':
    main()
