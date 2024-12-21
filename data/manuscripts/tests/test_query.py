import random
import pytest 
import data.manuscripts.query as mqry
import data.manuscripts.fields as flds
from data.tests.test_people import temp_person  # Import the fixture from test_people.py


TEST_TITLE = "Three Little Bears"
TEST_AUTHOR_NAME = 'Joe Smith'
TEST_REFEREE = 'bob@nyu.edu'

@pytest.fixture(scope='function')
def temp_manu(temp_person):
    title = mqry.create_manuscript( 
        TEST_TITLE,
        TEST_AUTHOR_NAME,
        temp_person,
        TEST_REFEREE,
        mqry.SUBMITTED,
        mqry.ACTIONS['ASSIGN_REF']
    )
    yield title
    try: 
        mqry.delete(title)
    except:
        print('Manuscript already deleted.')


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


def test_create_manuscript(temp_person):
    """
    Test creating a manuscript.
    """
    mqry.create_manuscript(TEST_TITLE, TEST_AUTHOR_NAME, temp_person, TEST_REFEREE, mqry.SUBMITTED, mqry.ACTIONS['ASSIGN_REF'])
    assert mqry.exists(TEST_TITLE)
    mqry.delete(TEST_TITLE)


def test_delete(temp_manu):
    """
    Test deleting a manuscript.
    """
    mqry.delete(temp_manu)
    assert not mqry.exists(temp_manu)


def test_get_manuscripts(temp_manu):
    """
    Test reading all manuscripts.
    """
    manuscripts = mqry.get_manuscripts() 
    assert isinstance(manuscripts, dict)
    assert len(manuscripts) > 0

    for _id, manuscript in manuscripts.items():
        assert isinstance(_id, str)
        assert isinstance(manuscript, dict)
        assert flds.TITLE in manuscript
        assert flds.AUTHOR in manuscript
        assert flds.AUTHOR_EMAIL in manuscript 
        assert flds.REFEREES in manuscript
        assert flds.STATE in manuscript
        assert flds.ACTION in manuscript
    
    assert temp_manu in manuscripts


def test_get_one_manu(temp_manu):
    """
    Test reading an existing manuscript.
    """
    assert mqry.get_one_manu(temp_manu) is not None


def test_exists(temp_manu):
    """
    Test checking if a manuscript exists.
    """
    assert mqry.exists(temp_manu)


def test_doesnt_exist():
    """
    Test checking if a manuscript does not exist.
    """
    assert not mqry.exists('Not an existing manuscript!')


def test_handle_action_bad_state():
    """
    Test handling actions with an invalid state.
    """
    invalid_state = gen_random_not_valid_str()
    try:
        mqry.handle_action(invalid_state, mqry.ACTIONS['ACCEPT'], 
                           manu=mqry.SAMPLE_MANU, ref='Some ref')
    except ValueError as e:
        assert str(e) == f'Invalid state: {invalid_state}'


def test_handle_action_bad_action():
    """
    Test handling actions with an invalid action.
    """
    invalid_action = gen_random_not_valid_str()
    try:
        mqry.handle_action(mqry.SUBMITTED, invalid_action, 
                           manu=mqry.SAMPLE_MANU, ref='Some ref')
    except ValueError as e:
        assert str(e) == f'Invalid action: {invalid_action}'
        
        
def test_handle_action_valid_return():
    for state in mqry.get_states():
        for action in mqry.get_actions():
            if state not in mqry.STATE_TABLE or action not in mqry.STATE_TABLE[state]:
                continue
            new_state = mqry.handle_action(state, action, manu=mqry.SAMPLE_MANU, ref='Some ref')
            assert mqry.is_valid_state(new_state)


def test_handle_action():
    """
    Test handling actions and state transitions.
    """
    assert mqry.handle_action(mqry.SUBMITTED, 
                              mqry.ACTIONS['ASSIGN_REF'],
                              manu=mqry.SAMPLE_MANU, 
                              ref='Some ref') == mqry.REFEREE_REVIEW
    assert mqry.handle_action(mqry.SUBMITTED, 
                              mqry.ACTIONS['REJECT'], 
                              manu=mqry.SAMPLE_MANU) == mqry.REJECTED
    assert mqry.handle_action(mqry.REFEREE_REVIEW, 
                              mqry.ACTIONS['ACCEPT'], 
                              manu=mqry.SAMPLE_MANU) == mqry.COPY_EDIT
    assert mqry.handle_action(mqry.REFEREE_REVIEW, 
                              mqry.ACTIONS['REJECT'], 
                              manu=mqry.SAMPLE_MANU) == mqry.REJECTED
    assert mqry.handle_action(mqry.REFEREE_REVIEW, 
                              mqry.ACTIONS['ACCEPT_WITH_REV'],
                              manu=mqry.SAMPLE_MANU) == mqry.AUTHOR_REVISION
    assert mqry.handle_action(mqry.REFEREE_REVIEW, 
                              mqry.ACTIONS['ASSIGN_REF'], 
                              manu=mqry.SAMPLE_MANU, 
                              ref='Some ref') == mqry.REFEREE_REVIEW
    assert mqry.handle_action(mqry.AUTHOR_REVISION, 
                              mqry.ACTIONS['DONE'], 
                              manu=mqry.SAMPLE_MANU) == mqry.EDITOR_REVIEW
    assert mqry.handle_action(mqry.EDITOR_REVIEW, 
                              mqry.ACTIONS['ACCEPT'], 
                              manu=mqry.SAMPLE_MANU) == mqry.COPY_EDIT
    assert mqry.handle_action(mqry.COPY_EDIT, 
                              mqry.ACTIONS['DONE'], 
                              manu=mqry.SAMPLE_MANU) == mqry.AUTHOR_REVIEW
    assert mqry.handle_action(mqry.AUTHOR_REVIEW, 
                              mqry.ACTIONS['DONE'], 
                              manu=mqry.SAMPLE_MANU) == mqry.FORMATTING
    assert mqry.handle_action(mqry.FORMATTING, 
                              mqry.ACTIONS['DONE'], 
                              manu=mqry.SAMPLE_MANU) == mqry.PUBLISHED
    assert mqry.handle_action(mqry.PUBLISHED, 
                              mqry.ACTIONS['DONE'], 
                              manu=mqry.SAMPLE_MANU) == mqry.PUBLISHED
    assert mqry.handle_action(mqry.REJECTED, 
                              mqry.ACTIONS['DONE'], 
                              manu=mqry.SAMPLE_MANU) == mqry.REJECTED
    assert mqry.handle_action(mqry.WITHDRAWN, 
                              mqry.ACTIONS['WITHDRAW'], 
                              manu=mqry.SAMPLE_MANU) == mqry.WITHDRAWN