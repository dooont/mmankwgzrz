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


def get_roles() -> dict:
    return deepcopy(ROLES)


def get_role_codes() -> list:
    return list(ROLES.keys())

# deletion of roles only happens in this module, this function
# def get_masthead_roles() -> dict:
#     mh_roles = get_roles()
#     del_mh_roles = []
#     for role in mh_roles:
#         if role not in MH_ROLES:
#             del_mh_roles.append(role)
#     for del_role in del_mh_roles:
#         del mh_roles[del_role]
#     return mh_roles


def is_valid(code: str) -> bool:
    return code in ROLES


def main():
    print(get_roles())


if __name__ == '__main__':
    main()