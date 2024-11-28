"""
This module provides a sample query form.
"""

import data.manuscripts.form_filler as ff

from data.manuscripts.form_filler import FLD_NM

USERNAME = 'username'
PASSWORD = 'password'

FORM_FLDS = [
    {
        FLD_NM: 'Instructions',
        ff.QSTN: 'Enter your username and password.',
        ff.INSTRUCTIONS: True,
    },
    {
        FLD_NM: USERNAME,
        ff.QSTN: 'User name:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
    {
        FLD_NM: PASSWORD,
        ff.QSTN: 'Password:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
]


def get_form() -> list:
    return FORM_FLDS


def get_form_descr():
    """
    For Swagger!
    """
    return ff.get_form_descr(FORM_FLDS)


def get_fld_names() -> list:
    return ff.get_fld_names(FORM_FLDS)


def main():
    # print(f'Form: {get_form()=}')
    print(f'Form: {get_form_descr()=}')
    # print(f'Field names: {get_fld_names()=}')


if __name__ == "__main__":
    main()