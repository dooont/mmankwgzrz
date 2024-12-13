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


def test_is_valid():
    assert mflds.is_valid(mflds.TEST_FLD_NM)
    assert not mflds.is_valid("NOT A VALID FIELD")


@pytest.fixture(scope='function')
def temp_field():
    field = 'TEST_FIELD'
    mflds.create_field(field, 'Test Field')
    yield field
    try:
        mflds.delete_field(field)
    except:
        print('Field already deleted.')


def test_create_field(temp_field):
    assert mflds.is_valid(temp_field)


def test_create_field_duplicate(temp_field):
    with pytest.raises(ValueError):
        mflds.create_field(temp_field, 'Other')


def test_update_field(temp_field):
    mflds.update_field(temp_field, 'New Name')
    assert mflds.get_disp_name(temp_field) == 'New Name'


def test_update_nonexistent_field():
    with pytest.raises(ValueError):
        mflds.update_field('NONEXISTENT_FIELD', 'New Name')


def test_delete_field(temp_field):
    mflds.delete_field(temp_field)
    assert not mflds.is_valid(temp_field)


def test_delete_nonexistent_field(temp_field):
    with pytest.raises(ValueError):
        mflds.delete_field('NONEXISTENT_FIELD')
