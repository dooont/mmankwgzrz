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


def get_form_descr() -> dict:
    """
    For Swagger!
    """
    return ff.get_form_descr(FORM_FLDS)


def get_fld_names() -> list:
    return ff.get_fld_names(FORM_FLDS)


def get_query_fld_names() -> list:
    return ff.get_query_fld_names(FORM_FLDS)


def update_form_field(field_name, question=None, param_type=None, optional=None) -> dict:
    fields = get_form()
    field = next((fld for fld in fields if fld[FLD_NM] == field_name), None)
    if not field:
        raise ValueError(f'Field with name {field_name} not found.')

    if question is not None:
        field[ff.QSTN] = question
    if param_type is not None:
        field[ff.PARAM_TYPE] = param_type
    if optional is not None:
        field[ff.OPT] = optional

    return field


def main():
    print(f'Form: {get_form()=}')
    print(f'Form: {get_form_descr()=}')
    print(f'Field names: {get_fld_names()=}')


if __name__ == "__main__":
    main()