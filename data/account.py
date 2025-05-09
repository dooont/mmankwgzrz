import bcrypt

import data.people as ppl
import data.db_connect as dbc


EMAIL = 'email'
PASSWORD = 'password'
ACCOUNT_COLLECT = 'account'
PEOPLE_COLLECT = 'people'

INVALID_LOGIN_MSG = "Invalid email or password"

client = dbc.connect_db()
print(f'{client=}')


def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def check_password(password: str, hashed_password: str) -> bool:
    """
    Compares a plain text password with a hashed password.
    """
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def change_password(new_password: str, email: str) -> bool:
    """
    Change password from old to new.
    """
    result = dbc.update(ACCOUNT_COLLECT, {EMAIL: email},
                        {PASSWORD: hash_password(new_password)})
    if result.matched_count > 0:
        return True
    return False


def is_valid_password(password: str) -> bool:
    """
    Validates password requirements:
    - At least 8 characters long
    - Contains at least one letter
    - Contains at least one digit
    """
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')

    if not any(char.isalpha() for char in password):
        raise ValueError('Password must contain at least one letter')

    if not any(char.isdigit() for char in password):
        raise ValueError('Password must contain at least one digit')

    return True


def register(email: str, password: str):
    """
    Register an account.
    - Ensure the email is valid and not already in the DB.
    - Ensure the password is at least 8 characters, has a letter, and
      has a digit.
    - Hash the password before storing it.
    """
    if not ppl.is_valid_email(email):
        raise ValueError(f'Email does not follow correct format: {email}')

    if dbc.read_one(ACCOUNT_COLLECT, {EMAIL: email}):
        raise ValueError(f'Account already exists for: {email}')

    if dbc.read_one(PEOPLE_COLLECT, {EMAIL: email}):
        raise ValueError(f'Person already exists for: {email}')

    if not is_valid_password(password):
        raise ValueError('Password is not valid')

    hashed_pw = hash_password(password)
    account = {EMAIL: email, PASSWORD: hashed_pw}
    dbc.create(ACCOUNT_COLLECT, account)
    return email


def login(email: str, password: str) -> bool:
    """
    Logs in a user by verifying their email and password.
    """
    account = dbc.read_one(ACCOUNT_COLLECT, {EMAIL: email})

    if not account or not check_password(password, account[PASSWORD]):
        raise ValueError(INVALID_LOGIN_MSG)

    return True


def get_password(email: str):
    account = dbc.read_one(ACCOUNT_COLLECT, {EMAIL: email})
    return account[PASSWORD]


def delete(email: str) -> int:
    """
    Deletes a user's account.
    """
    account = dbc.read_one(ACCOUNT_COLLECT, {EMAIL: email})

    if not account:
        raise ValueError('Account does not exist')

    return dbc.delete(ACCOUNT_COLLECT, {EMAIL: email}) > 0
