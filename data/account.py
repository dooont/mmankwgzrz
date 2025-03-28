import bcrypt

import data.people as ppl
import data.db_connect as dbc


EMAIL = 'email'
PASSWORD = 'password'
ACCOUNT_COLLECT = 'account'

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

    is_valid_password(password)

    hashed_pw = hash_password(password)
    account = {EMAIL: email, PASSWORD: hashed_pw}
    dbc.create(ACCOUNT_COLLECT, account)
    return email


def login(email: str, password: str) -> bool:
    """
    Logs in a user by verifying their email and password.
    """
    account = dbc.read_one(ACCOUNT_COLLECT, {EMAIL: email})

    if not account:
        raise ValueError('Account does not exist')

    if not check_password(password, account[PASSWORD]):
        raise ValueError('Incorrect password')

    return True


def delete(email: str) -> bool:
    """
    Deletes a user's account.
    """
    account = dbc.read_one(ACCOUNT_COLLECT, {EMAIL: email})

    if not account:
        raise ValueError('Account does not exist')

    return dbc.delete(ACCOUNT_COLLECT, {EMAIL: email}) > 0
