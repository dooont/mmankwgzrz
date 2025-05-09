import pytest

import data.db_connect as dbc
import data.account as acc


TEST_EMAIL = 'test_person@nyu.com'
TEST_PASSWORD = 'password123'
INVALID_EMAIL = 'invalid_email@'
INVALID_PASSWORD = 'short'
TEMP_EMAIL = 'temp_person@temp.org'
NONEXISTENT_EMAIL = 'nonexistent@example.com'

ACCOUNT = 'account'
EMAIL = 'email'
ACCOUNT_COLLECT = 'account'


@pytest.fixture(scope='function')
def temp_account():
    email = acc.register(TEMP_EMAIL, TEST_PASSWORD)
    yield email
    try:
        acc.delete(email)
    except:
        print(f'Account already deleted.')


def test_register_account():
    email = acc.register(TEST_EMAIL, TEST_PASSWORD)
    assert email == TEST_EMAIL

    account_data = dbc.read_one(ACCOUNT_COLLECT, {EMAIL: TEST_EMAIL})
    assert account_data is not None
    assert account_data[EMAIL] == TEST_EMAIL

    acc.delete(TEST_EMAIL)


def test_register_account_invalid_email():
    with pytest.raises(ValueError):
        acc.register(INVALID_EMAIL, TEST_PASSWORD)


def test_register_account_invalid_password():
    with pytest.raises(ValueError):
        acc.register(TEST_EMAIL, INVALID_PASSWORD)


def test_register_duplicate_account():
    acc.register(TEST_EMAIL, TEST_PASSWORD)

    with pytest.raises(ValueError):
        acc.register(TEST_EMAIL, TEST_PASSWORD)

    acc.delete(TEST_EMAIL)


def test_login_successful(temp_account):
    result = acc.login(temp_account, TEST_PASSWORD)
    assert result is True


def test_login_failed():
    with pytest.raises(ValueError):
        acc.login(TEST_EMAIL, 'WrongPassword')


def test_login_account_not_found():
    with pytest.raises(ValueError):
        acc.login(NONEXISTENT_EMAIL, TEST_PASSWORD)


def test_delete_account(temp_account):
    result = acc.delete(temp_account)
    assert result is True

    account_data = dbc.read_one(ACCOUNT_COLLECT, {EMAIL: temp_account})
    assert account_data is None


def test_delete_account_failed():
    with pytest.raises(ValueError):
        acc.delete(NONEXISTENT_EMAIL)


def test_is_valid_password():
    result = acc.is_valid_password(TEST_PASSWORD)
    assert result is True


def test_is_valid_password_invalid():
    # Too short
    with pytest.raises(ValueError):
        acc.is_valid_password('short')

    # No letter
    with pytest.raises(ValueError):
        acc.is_valid_password('12345678')

    # No digit
    with pytest.raises(ValueError):
        acc.is_valid_password('abcdefgh')
