TEST_FLD_DISP_NM = 'Title'
TEST_FLD_NM = 'title'

DISP_NAME = 'disp_name'

TITLE = 'title'
AUTHOR = 'author'
REFEREES = 'referees'
AUTHOR_EMAIL = 'author email'
STATE = 'state'
TEXT = 'text'
ABSTRACT = 'abstract'
HISTORY = 'history'
EDITOR = 'Editor'


FIELDS = {
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


def create_field(fld: str, disp_nm: str):
    if is_valid(fld):
        raise ValueError(f'Adding duplicate field: {fld=}')
    FIELDS[fld] = {DISP_NAME: disp_nm}


def update_field(fld: str, disp_nm: str):
    if not is_valid(fld):
        raise ValueError(f'Adding nonexistent field: {fld=}')
    FIELDS[fld][DISP_NAME] = disp_nm


"""
def get_authors(field: str=AUTHOR) -> str:
    if field == AUTHOR:
        return FIELDS[AUTHOR][DISP_NAME]
    return ''


def get_referees(field: str=REFEREES) -> list:
    if field == REFEREES:
        return FIELDS[REFEREES][DISP_NAME]
    return []
"""


def main():
    print(f'{get_flds()=}')


if __name__ == '__main__':
    main()