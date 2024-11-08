import pytest
import data.roles as rls


@pytest.fixture
def roles_data():
    return rls.get_roles()


@pytest.fixture
def masthead_roles_data():
    return rls.get_masthead_roles()


def test_get_roles(roles_data):
    assert isinstance(roles_data, dict)
    assert len(roles_data) > 0
    for code, role in roles_data.items():
        assert isinstance(code, str)
        assert isinstance(role, str)


def test_get_masthead_roles(masthead_roles_data):
    assert isinstance(masthead_roles_data, dict)
    assert set(masthead_roles_data.keys()).issubset(rls.MH_ROLES)


def test_get_role_codes():
    codes = rls.get_role_codes()
    assert isinstance(codes, list)
    for code in codes:
        assert isinstance(code, str)


def test_is_valid():
    assert rls.is_valid(rls.TEST_CODE)
    assert not rls.is_valid("NOT A VALID ROLE")
