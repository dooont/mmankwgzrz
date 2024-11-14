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
