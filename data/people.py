"""
This module interfaces to our user data.
"""
# importing python re module to match email strings based on patterns
import re
import data.roles as rls
import data.db_connect as dbc

PEOPLE_COLLECT = 'people'

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
        ROLES: [rls.ED_CODE],
        AFFILIATION: 'NYU',
        EMAIL: TEST_EMAIL
    },
    DEL_EMAIL: {
        NAME: 'Jeffrey Person',
        ROLES: [rls.CE_CODE],
        AFFILIATION: 'NYU',
        EMAIL: DEL_EMAIL,
    },
}


client = dbc.connect_db()
print(f'{client=}')


EMAIL_FORMAT = (
            r'^[A-Za-z0-9]+'            # Start with alnum characters
            r'([_.+-][a-zA-Z0-9]+)*'    # Allow ., +, - followed by alnum char
            r'@[a-zA-Z0-9]+'            # "@" symbol followed by domain name
            r'([.-][a-zA-Z0-9]+)*'      # Allow for subdomains
            r'\.[a-zA-Z]{2,}$'          # End with TLD (min length of 2)
        )


def is_valid_email(email):
    if isinstance(email, str):
        if re.match(EMAIL_FORMAT, email):
            return True
        else:
            raise ValueError(f'Email does not follow correct format: {email}')
    else:
        raise ValueError(f'Email is not a string: {email}')


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str = None, roles: list = None) -> bool:
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


def read() -> dict:
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each email must be the key for another dictionary.
    """
    people = dbc.read_dict(PEOPLE_COLLECT, EMAIL)
    print(f'{people=}')
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


def create(name: str, affiliation: str, email: str, role: str):
    if email in people_dict:
        raise ValueError(f'Adding duplicate email: {email=}')
    if is_valid_person(name, affiliation, email, role):
        roles = []
        if role:
            roles.append(role)
        people_dict[email] = {NAME: name, ROLES: roles,
                              AFFILIATION: affiliation, EMAIL: email}
        print(person)
        dbc.create(PEOPLE_COLLECT, person)
        return email


def update(name: str, affiliation: str, old_email: str, new_email: str,
           roles: list):
    if old_email not in people_dict:
        raise ValueError(f'Updating non-existent person: {old_email=}')
    if is_valid_person(name, affiliation, new_email, roles=roles):
        people_dict[new_email] = {NAME: name, AFFILIATION: affiliation,
                                  EMAIL: new_email, ROLES: roles}
        if old_email != new_email:
            del people_dict[old_email]
        return new_email


def has_role(person: dict, role: str) -> bool:
    if role in person[ROLES]:
        return True
    return False


MH_FIELDS = [NAME, AFFILIATION]


def get_mh_fields(journal_code=None) -> list:
    return MH_FIELDS


def create_mh_rec(person: dict) -> dict:
    mh_rec = {}
    for field in get_mh_fields():
        mh_rec[field] = person.get(field, '')
    return mh_rec


def get_masthead() -> dict:
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for mh_role, text in mh_roles.items():
        print(f'{mh_role=}')
        people_w_role = []  # an array of people with role
        people = read()
        for _id, person in people.items():
            if has_role(person, mh_role):
                rec = create_mh_rec(person)
                # Put their record in people_w_role
                people_w_role.append(rec)
        masthead[text] = people_w_role
    return masthead


def main():
    print(read())


if __name__ == '__main__':
    main()
