"""
This module manages person roles for a journal
"""
from copy import deepcopy

AUTHOR_CODE = 'AU'
CE_CODE = 'CE'
ED_CODE = 'ED'
ME_CODE = 'ME'
TEST_CODE = AUTHOR_CODE

ROLES = {
    AUTHOR_CODE: 'Author',
    CE_CODE: 'Consulting Editor',
    ED_CODE: 'Editor',
    ME_CODE: 'Managing Editor',
    'RE': 'Referee',
}

MH_ROLES = [CE_CODE, ED_CODE, ME_CODE]


# This function gets the roles
def get_roles() -> dict:
    return deepcopy(ROLES)


# This function gets the role codes
def get_role_codes() -> list:
    return list(ROLES.keys())


# deletion of roles only happens in this module, this function
def get_masthead_roles() -> dict:
    mh_roles = get_roles()
    del_mh_roles = []
    for role in mh_roles:
        if role not in MH_ROLES:
            # if roles are not masthead roles then delete
            # by appending to array of roles to be removed
            del_mh_roles.append(role)
    for del_role in del_mh_roles:
        # search through mh_roles to find keys of roles to be deleted
        del mh_roles[del_role]
    # returned mh_roles should contain only mh_roles
    return mh_roles


# This function checks if the code is valid
def is_valid(code: str) -> bool:
    return code in ROLES


# General main function for running the code
def main():
    print(get_roles())


if __name__ == '__main__':
    main()
