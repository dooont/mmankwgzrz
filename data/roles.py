"""
This module manages person roles for a journal.
"""
from copy import deepcopy

AUTHOR_CODE = 'AU'
CE_CODE = 'CE'
ED_CODE = 'ED'
ME_CODE = 'ME'
RE_CODE = 'RE'
TEST_CODE = AUTHOR_CODE

ROLES = {
    AUTHOR_CODE: 'Author',
    CE_CODE: 'Consulting Editor',
    ED_CODE: 'Editor',
    ME_CODE: 'Managing Editor',
    RE_CODE: 'Referee',
}

MH_ROLES = [CE_CODE, ED_CODE, ME_CODE]


def get_roles() -> dict:
    """
    Returns a copy of the ROLES dictionary.
    """
    return deepcopy(ROLES)


def get_role_codes() -> list:
    """
    Returns a list of all role codes from the ROLES dictionary.
    """
    return list(ROLES.keys())


def role_in_mh_roles(role: str) -> bool:
    """
    Checks if a given role code is part of the masthead roles.
    """
    return role in MH_ROLES


def get_masthead_roles() -> dict:
    """
    Filters and returns only the masthead roles from the ROLES dictionary.
    Non-masthead roles are removed from the result.
    """
    mh_roles = get_roles()
    del_mh_roles = []

    # Identify roles to delete (those not in masthead roles).
    for role in mh_roles:
        if not role_in_mh_roles(role):
            del_mh_roles.append(role)

    # Remove the identified non-masthead roles.
    for del_role in del_mh_roles:
        del mh_roles[del_role]

    return mh_roles


def is_valid(code: str) -> bool:
    """
    Validates if a given code exists in the ROLES dictionary.
    """
    return code in ROLES


def main():
    print(get_roles())
    print(get_masthead_roles())


if __name__ == '__main__':
    main()
