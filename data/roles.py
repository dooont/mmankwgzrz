"""
This module manages person roles for a journal
"""
from copy import deepcopy

AUTHOR_CODE = 'AU'
TEST_CODE = AUTHOR_CODE
ED_CODE = 'ED'
ME_CODE = 'ME'
CE_CODE = 'CE'

ROLES = {
    AUTHOR_CODE: 'Author',
    CE_CODE: 'Consulting Editor',
    ED_CODE: 'Editor',
    ME_CODE: 'Managing Editor',
    'RE': 'Referee',
}


def get_roles() -> dict:
    return deepcopy(ROLES)


def get_role_codes() -> list:
    return list(ROLES.keys())


def is_valid(code: str) -> bool:
    return code in ROLES


def main():
    print(get_roles())


if __name__ == '__main__':
    main()
