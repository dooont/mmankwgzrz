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


def test_get_authors():
    ret = mflds.get_authors()
    assert isinstance(ret, list)
    assert mflds.AUTHOR in ret
    ret = mflds.get_authors('not_author')
    assert ret == []
    assert isinstance(ret, list)


def test_get_referees():
    ret = mflds.get_referees()
    assert isinstance(ret, list)
    assert mflds.REFEREES in ret
    ret = mflds.get_referees('not_referee')
    assert ret == []
    assert isinstance(ret, list)


def test_is_valid():
    assert mflds.is_valid(mflds.TEST_FLD_NM)
    assert not mflds.is_valid("NOT A VALID FIELD")


def test_create_author():
    mflds.create_author('JOE SMITH')
    assert mflds.author_exists('JOE SMITH')


def test_create_referee():
    mflds.create_referee('JOE SMITH')
    assert mflds.author_exists('JOE SMITH')


# crude until delete functionality is created
def test_create_author_duplicate():
    mflds.create_author('TEMP')
    with pytest.raises(ValueError):
        mflds.create_author('TEMP')


def test_create_referee_duplicate():
    mflds.create_referee('TEMP')
    with pytest.raises(ValueError):
        mflds.create_referee('TEMP')