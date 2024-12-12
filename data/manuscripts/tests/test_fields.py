import pytest

import data.manuscripts.fields as mflds


def test_get_flds():
    assert isinstance(mflds.get_flds(), dict)


def test_get_fld_names():
    ret = list(mflds.get_fld_names())
    assert isinstance(ret, list)
    assert mflds.TITLE in ret


def test_get_disp_name():
    ret = mflds.get_disp_name(mflds.TITLE)
    assert isinstance(ret, str)
    assert ret == mflds.TEST_FLD_DISP_NM
    assert mflds.get_disp_name('nonexistent_field') == None


# Will add fixture for these
def test_is_valid():
    assert mflds.is_valid(mflds.TEST_FLD_NM)
    assert not mflds.is_valid("NOT A VALID FIELD")


def test_create_field():
    mflds.create_field('TEST_FIELD', 'Test Field')
    assert mflds.is_valid('TEST_FIELD')


def test_create_field_duplicate():
    mflds.create_field('TEMP', 'Temp')
    with pytest.raises(ValueError):
        mflds.create_field('TEMP', 'Other')


def test_update_field():
    mflds.create_field('NEW_FIELD', 'Original Name')
    assert mflds.is_valid('NEW_FIELD')
    mflds.update_field('NEW_FIELD', 'New Name')
    assert mflds.get_disp_name('NEW_FIELD') == 'New Name'


def test_update_nonexistent_field():
    with pytest.raises(ValueError):
        mflds.update_field('NONEXISTENT_FIELD', 'New Name')

"""
def test_get_authors():
    ret = mflds.get_authors()
    assert isinstance(ret, str)
    ret = mflds.get_authors('not_author')
    assert ret == ''
    assert isinstance(ret, str)


def test_get_referees():
    ret = mflds.get_referees()
    assert isinstance(ret, list)
    assert mflds.REFEREES in ret
    ret = mflds.get_referees('not_referee')
    assert ret == []
    assert isinstance(ret, list)
"""