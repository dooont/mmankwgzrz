import random

import data.manuscripts.query as mqry


def gen_random_not_valid_str() -> str:
    """
    Generating a random big number that is known to not
    be a valid state or action.
    """
    BIG_NUM = 10_000_000_000
    big_int = random.randint(0, BIG_NUM)
    big_int += BIG_NUM
    bad_str = str(big_int)
    return bad_str


def test_is_valid_state():
    """
    Test the validity of all predefined states.
    """
    for state in mqry.get_states():
        assert mqry.is_valid_state(state)


def test_is_not_valid_state():
    """
    Test the invalidity of randomly generated strings.
    """
    for i in range(10):
        assert not mqry.is_valid_state(gen_random_not_valid_str())
