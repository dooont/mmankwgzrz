
TITLE = 'title'
DISP_NAME = 'disp_name'

TEST_FLD_NM = 'title'
TEST_FLD_DISP_NM = 'Title'


FIELDS = {
    TITLE: {
        DISP_NAME: TEST_FLD_DISP_NM,
    },
}


def get_flds() -> dict:
    return FIELDS


def get_fld_names() -> list:
    return FIELDS.keys()


def get_disp_name(fld_nm: str) -> dict:
    fld = FIELDS.get(fld_nm, '')
    return fld.get(DISP_NAME) # should we use get() here?


def is_valid(field: str) -> bool:
    return field in FIELDS


def main():
    print(f'{get_flds()=}')


if __name__ == '__main__':
    main()