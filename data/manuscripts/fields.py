from typing import Union

TEST_FLD_DISP_NM = 'Title'
TEST_FLD_NM = 'title'

DISP_NAME = 'disp_name'

ID = '_id'
TITLE = 'title'
AUTHOR = 'author'
REFEREES = 'referees'
AUTHOR_EMAIL = 'author_email'
STATE = 'state'
ACTION = 'action'
TEXT = 'text'
ABSTRACT = 'abstract'
HISTORY = 'history'
EDITOR = 'editor'
CURR_STATE = 'curr_state'


FIELDS = {
    ID :{
        DISP_NAME: 'ID',
    },
    TITLE: {
        DISP_NAME: 'Title',
    },
    AUTHOR: {
        DISP_NAME: 'Author',
    },
    REFEREES: {
        DISP_NAME: 'Referees',
    },
    AUTHOR_EMAIL: {
        DISP_NAME: 'Author Email',
    },
    STATE: {
        DISP_NAME: 'State',
    },
    TEXT: {
        DISP_NAME: 'Text',
    },
    ABSTRACT: {
        DISP_NAME: 'Abstract',
    },
    HISTORY: {
        DISP_NAME: 'History',
    },
    EDITOR: {
        DISP_NAME: 'Editor',
    },
}


def get_flds() -> dict:
    return FIELDS


def get_fld_names() -> list:
    return FIELDS.keys()


def get_disp_name(fld_nm: str) -> dict:
    fld = FIELDS.get(fld_nm, '')
    if fld:
        return fld.get(DISP_NAME) # should we use get() here?


def is_valid(field: str) -> bool:
    return field in FIELDS


def create_field(fld: str, disp_nm: str) -> Union[None, ValueError]:
    if is_valid(fld):
        raise ValueError(f'Adding duplicate field: {fld=}')
    FIELDS[fld] = {DISP_NAME: disp_nm}


def update_field(fld: str, disp_nm: str) -> Union[None, ValueError]:
    if not is_valid(fld):
        raise ValueError(f'Updating nonexistent field: {fld=}')
    FIELDS[fld][DISP_NAME] = disp_nm


def delete_field(fld: str) -> Union[None, ValueError]:
    if not is_valid(fld):
        raise ValueError(f'Deleting nonexistent field: {fld=}')
    del FIELDS[fld]


def main():
    print(f'{get_flds()=}')


if __name__ == '__main__':
    main()