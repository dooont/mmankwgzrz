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


def test_get_authors():
    ret = mflds.get_authors()
    assert isinstance(ret, list)
    assert mflds.AUTHOR in ret


def test_get_referees():
    ret = mflds.get_referees()
    assert isinstance(ret, list)
    assert mflds.REFEREES in ret


def test_is_valid():
    assert mflds.is_valid(mflds.TEST_FLD_NM)
    assert not mflds.is_valid("NOT A VALID FIELD")