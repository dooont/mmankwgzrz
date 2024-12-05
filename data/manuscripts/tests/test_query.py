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


def test_get_actions():
    """
    Test the retrieval of all predefined actions.
    """
    actions = mqry.get_actions()
    assert isinstance(actions, list)
    assert set(actions) == set(mqry.VALID_ACTIONS)


def test_is_valid_action():
    """
    Test the validity of all predefined actions.
    """
    for action in mqry.get_actions():
        assert mqry.is_valid_action(action)


def test_is_not_valid_action():
    """
    Test the invalidity of randomly generated strings.
    """
    for i in range(10):
        assert not mqry.is_valid_action(gen_random_not_valid_str())


def test_handle_action():
    """
    Test handling actions and state transitions.
    """
    assert mqry.handle_action(mqry.SUBMITTED, mqry.ACTIONS['ASSIGN_REF']) == mqry.REFEREE_REVIEW
    assert mqry.handle_action(mqry.SUBMITTED, mqry.ACTIONS['REJECT']) == mqry.REJECTED
    assert mqry.handle_action(mqry.REFEREE_REVIEW, mqry.ACTIONS['ACCEPT']) == mqry.COPY_EDIT
    assert mqry.handle_action(mqry.REFEREE_REVIEW, mqry.ACTIONS['REJECT']) == mqry.REJECTED
    assert mqry.handle_action(mqry.REFEREE_REVIEW, mqry.ACTIONS['ACCEPT_WITH_REV']) == mqry.AUTHOR_REVISION
    assert mqry.handle_action(mqry.AUTHOR_REVISION, mqry.ACTIONS['DONE']) == mqry.EDITOR_REVIEW
    assert mqry.handle_action(mqry.EDITOR_REVIEW, mqry.ACTIONS['ACCEPT']) == mqry.COPY_EDIT
    assert mqry.handle_action(mqry.COPY_EDIT, mqry.ACTIONS['DONE']) == mqry.AUTHOR_REVIEW
    assert mqry.handle_action(mqry.AUTHOR_REVIEW, mqry.ACTIONS['DONE']) == mqry.FORMATTING
    assert mqry.handle_action(mqry.FORMATTING, mqry.ACTIONS['DONE']) == mqry.PUBLISHED


def test_handle_action_bad_state():
    """
    Test handling actions with an invalid state.
    """
    invalid_state = gen_random_not_valid_str()
    try:
        mqry.handle_action(invalid_state, mqry.ACTIONS['ACCEPT'])
    except ValueError as e:
        assert str(e) == f'Invalid state: {invalid_state}'


def test_handle_action_bad_action():
    """
    Test handling actions with an invalid action.
    """
    invalid_action = gen_random_not_valid_str()
    try:
        mqry.handle_action(mqry.SUBMITTED, invalid_action)
    except ValueError as e:
        assert str(e) == f'Invalid action: {invalid_action}'
        
        
def test_handle_action_valid_return():
    for state in mqry.get_states():
        for action in mqry.get_actions():
            if state not in mqry.STATE_TABLE or action not in mqry.STATE_TABLE[state]:
                continue
            new_state = mqry.handle_action(state, action)
            assert mqry.is_valid_state(new_state)
