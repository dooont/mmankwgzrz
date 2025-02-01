"""
This module interfaces to our user data.
"""
import re   # Module for regular expressions, used for validating email format.
from typing import Union

import data.roles as rls
import data.db_connect as dbc


# Fields for person data
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'
MH_FIELDS = [NAME, AFFILIATION]  # Fields for masthead records

TEST_EMAIL = 'ejc369@nyu.edu'
DEL_EMAIL = 'delete@nyu.edu'

PEOPLE_COLLECT = 'people'

client = dbc.connect_db()
print(f'{client=}')


EMAIL_FORMAT = (
            r'^[A-Za-z0-9]+'            # Start with alnum characters
            r'([_.+-][a-zA-Z0-9]+)*'    # Allow ., +, - followed by alnum char
            r'@[a-zA-Z0-9]+'            # "@" symbol followed by domain name
            r'([.-][a-zA-Z0-9]+)*'      # Allow for subdomains
            r'\.[a-zA-Z]{2,}$'          # End with TLD (min length of 2)
        )


def is_valid_email(email: str) -> Union[bool, ValueError]:
    """
    Validates if the provided email matches the expected format.
    Raises ValueError if the email is invalid.
    """
    if isinstance(email, str):
        if re.fullmatch(EMAIL_FORMAT, email):
            return True
        else:
            raise ValueError(f'Email does not follow correct format: {email}')
    else:
        raise ValueError(f'Email is not a string: {email}')


def is_valid_person(name: str, affiliation: str, email: str, role: str = None,
                    roles: list = None) -> Union[bool, Exception]:
    """
    Validates person attributes.
        - The email is valid.
        - The role(s) are valid if provided.
    """
    if not is_valid_email(email):
        raise Exception(f'Invalid email: {email}')

    if role:
        if not rls.is_valid(role):
            raise Exception(f'Invalid role: {role}')
    elif roles:
        for role in roles:
            if not rls.is_valid(role):
                raise Exception(f'Invalid role: {role}')

    return True


def read() -> dict[str, dict]:
    """
    Reads all people data from the database.
    Returns:
        A dictionary where each key is an email, and the value is a dictionary
        of person data.
    """
    people = dbc.read_dict(PEOPLE_COLLECT, EMAIL)
    print(f'{people=}')
    return people


def read_one(email: str) -> dict:
    """
    Reads a single person record by email.
    Returns:
        A dictionary if the email exists, otherwise None.
    """
    return dbc.read_one(PEOPLE_COLLECT, {EMAIL: email})


def exists(email: str) -> bool:
    """
    Checks if a person with the given email exists in the database.
    """
    return read_one(email) is not None


def delete(email: str) -> int:
    """
    Deletes a person by email from the database.
    """
    print(f'{EMAIL=}, {email=}')
    return dbc.delete(PEOPLE_COLLECT, {EMAIL: email})


def delete_role(email: str, role: str) -> None:
    """
    Deletes a specific role for a person by email.
    """
    person = exists(email)
    if person:
        status = dbc.delete_role(PEOPLE_COLLECT, {EMAIL: email}, {ROLES: role})
        if status:
            print('Role successfully deleted')
        else:
            print('Role of person could not be found')
    else:
        print('Person not found!')


def create(name: str, affiliation: str, email: str, role: str) \
                                        -> Union[str, ValueError]:
    """
    Creates a new person in the database.
    Raises ValueError if the email already exists.
    """
    if exists(email):
        raise ValueError(f'Adding duplicate email: {email=}')

    if is_valid_person(name, affiliation, email, role):
        roles = [role] if role else []
        person = {NAME: name, ROLES: roles,
                  AFFILIATION: affiliation, EMAIL: email}
        print(person)
        dbc.create(PEOPLE_COLLECT, person)
        return email


def update(name: str, affiliation: str, email: str, roles: list) \
                                        -> Union[str, ValueError]:
    """
    Updates an existing person's details in the database.
    Raises ValueError if the person does not exist.
    """
    if not exists(email):
        raise ValueError(f'Updating non-existent person: {email=}')

    if is_valid_person(name, affiliation, email, roles=roles):
        person = {NAME: name, AFFILIATION: affiliation,
                  EMAIL: email, ROLES: roles}
        print(person)
        dbc.update(PEOPLE_COLLECT, {EMAIL: email}, person)
        return email


def has_role(person: dict, role: str) -> bool:
    """
    Checks if a person has a specific role.
    """
    if role in person[ROLES]:
        return True
    return False


def get_mh_fields() -> list[str]:
    """
    Returns fields to include in masthead records.
    """
    return MH_FIELDS


def create_mh_rec(person: dict) -> dict:
    """
    Creates a masthead record for a person.
    """
    mh_rec = {}
    for field in get_mh_fields():
        mh_rec[field] = person.get(field, '')
    return mh_rec


def get_masthead() -> dict[str, list[dict]]:
    """
    Compiles a masthead dictionary grouping people by their masthead roles.
    """
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for mh_role, text in mh_roles.items():
        print(f'{mh_role=}')
        people_w_role = []
        people = read()
        for email, person in people.items():
            if has_role(person, mh_role):
                rec = create_mh_rec(person)
                people_w_role.append(rec)
        masthead[text] = people_w_role
    return masthead


def main():
    print(read())
    print(get_masthead())


if __name__ == '__main__':
    main()
