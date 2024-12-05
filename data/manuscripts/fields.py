
TITLE = 'title'
DISP_NAME = 'disp_name'

TEST_FLD_NM = 'title'
TEST_FLD_DISP_NM = 'Title'

AUTHOR = 'author'
REFEREES = 'referees'

FIELDS = {
    TITLE: {
        DISP_NAME: TEST_FLD_DISP_NM,
    },
    AUTHOR: {
        DISP_NAME: [AUTHOR],
    },
    REFEREES: {
        DISP_NAME: [REFEREES],
    }
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


def get_authors(field: str=AUTHOR) -> dict:
    if field == AUTHOR:
        return FIELDS[AUTHOR][DISP_NAME]
    return []


def get_referees(field: str=REFEREES) -> dict:
    if field == REFEREES:
        return FIELDS[REFEREES][DISP_NAME]
    return []


def main():
    print(f'{get_flds()=}')


if __name__ == '__main__':
    main()