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


people_dict = {
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


def read() -> dict:
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each email must be the key for another dictionary.
    """
    people = people_dict
    return people


def read_one(email: str) -> dict:
    """
    Return a person record if email present in DB,
    else None.
    """
    return people_dict.get(email)


def delete(_id):
    people = read()
    if _id in people:
        del people[_id]
        return _id
    else:
        return None


def is_valid_email(email):
    if isinstance(email, str):
        email_format = (
            r'^[a-zA-Z0-9]+'            # Start with alnum characters
            r'([_.+-][a-zA-Z0-9]+)*'    # Allow ., +, - followed by alnum char
            r'@[a-zA-Z0-9]+'            # "@" symbol followed by domain name
            r'([.-][a-zA-Z0-9]+)*'      # Allow for subdomains
            r'\.[a-zA-Z]{2,}$'          # End with TLD (min length of 2)
        )
        if re.match(email_format, email):
            return True
        else:
            raise ValueError(f'Email does not follow correct format: {email}')
    else:
        raise ValueError(f'Email is not a string: {email}')


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str = None, roles: list = None) -> bool:
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if role:
        if not rls.is_valid(role):
            raise ValueError(f'Invalid role: {role}')
    elif roles:
        for role in roles:
            if not rls.is_valid(role):
                raise ValueError(f'Invalid role: {role}')
    return True


def create(name: str, affiliation: str, email: str, role: str):
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if is_valid_person(name, affiliation, email, role):
        roles = []
        if role:
            roles.append(role)
        people_dict[email] = {NAME: name, ROLES: roles,
                              AFFILIATION: affiliation, EMAIL: email}
        return email


def update(name: str, affiliation: str, email: str, roles: list):
    if email not in people_dict:
        raise ValueError(f'Updating non-existent person: {email=}')
    if is_valid_person(name, affiliation, email, roles=roles):
        people_dict[email] = {NAME: name, AFFILIATION: affiliation,
                              EMAIL: email, ROLES: roles}
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
