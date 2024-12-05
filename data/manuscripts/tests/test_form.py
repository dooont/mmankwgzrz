import data.manuscripts.form as mform


def test_get_form():
    assert isinstance(mform.get_form(), list)


def test_get_form_descr():
    form_descr = mform.get_form_descr()
    assert isinstance(form_descr, dict)
    for item in form_descr:
        assert isinstance(item, str )
        assert 'username' or 'password' in item


def test_get_fld_names():
    fld_names = mform.get_fld_names()
    assert isinstance(fld_names, list)
    assert all(isinstance(name, str) for name in fld_names)


def test_get_query_fld_names():
    query_fld_names = mform.get_query_fld_names()
    assert isinstance(query_fld_names, list)
    assert all(isinstance(name, str) for name in query_fld_names)


def test_valid_forms():
    for form in mform.get_form():
        assert isinstance(form, dict)