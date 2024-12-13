import pytest

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

        
def test_update_form_field():
    # Test updating question
    updated_field = mform.update_form_field('username', question='New User name:')
    assert updated_field[mform.ff.QSTN] == 'New User name:'

    # Test updating param_type
    updated_field = mform.update_form_field('password', param_type=mform.ff.QUERY_STR)
    assert updated_field[mform.ff.PARAM_TYPE] == mform.ff.QUERY_STR

    # Test updating optional
    updated_field = mform.update_form_field('username', optional=True)
    assert updated_field[mform.ff.OPT] is True

    # Test updating multiple fields
    updated_field = mform.update_form_field('password', question='New Password:', param_type=mform.ff.QUERY_STR, optional=True)
    assert updated_field[mform.ff.QSTN] == 'New Password:'
    assert updated_field[mform.ff.PARAM_TYPE] == mform.ff.QUERY_STR
    assert updated_field[mform.ff.OPT] is True

    # Test field not found
    with pytest.raises(ValueError, match='Field with name non_existent_field not found.'):
        mform.update_form_field('non_existent_field', question='Should fail')
