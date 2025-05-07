import random
import copy
import pytest

import data.manuscripts.query as mqry
import data.manuscripts.fields as flds
import data.people as ppl
import data.roles as rls

# Import the fixture from test_people.py
from data.tests.test_people import temp_person

from bson import ObjectId

# Constants
TEST_TITLE = "Three Little Bears"
TEST_AUTHOR_NAME = 'Joe Smith'
TEST_REFEREE = 'bob@nyu.edu'
TEST_NEW_REFEREE = 'alice@nyu.edu'
TEST_TEXT = "Hi my name is Andy"
TEST_ABSTRACT = "This is the Abstract"


@pytest.fixture(scope='function')
def temp_manu(temp_person):
    id = mqry.create_manuscript(
        TEST_TITLE,
        TEST_AUTHOR_NAME,
        temp_person,
        TEST_REFEREE,
        mqry.SUBMITTED,
        TEST_TEXT,
        TEST_ABSTRACT,
    )
    yield id
    try:
        mqry.delete(id)
    except:
        print('Manuscript already deleted.')


@pytest.fixture(scope='function')
def temp_referee():
    email = "referee@example.com"
    name = "Referee User"
    affiliation = "NYU"
    roles = [rls.RE_CODE]

    if not ppl.exists(email):
        ppl.create(name, affiliation, email, roles)
    else:
        person = ppl.read_one(email)
        ppl.update(person[ppl.NAME], person[ppl.AFFILIATION], email, roles)

    yield email

    try:
        ppl.delete(email)
    except Exception:
        print("Referee already deleted.")


@pytest.fixture(scope='function')
def temp_ref_manu(temp_person, temp_referee):
    manu_id = mqry.create_manuscript(
        "Ref Manuscript",
        "Test Author",
        temp_person,
        temp_referee,
        mqry.SUBMITTED,
        "Ref text",
        "Ref abstract"
    )
    yield manu_id
    try:
        mqry.delete(manu_id)
    except Exception:
        print("Ref manuscript already deleted.")


def gen_random_not_valid_str() -> str:
    BIG_NUM = 10_000_000_000
    return str(random.randint(BIG_NUM, BIG_NUM * 2))


def test_is_valid_state():
    for state in mqry.get_states():
        assert mqry.is_valid_state(state)


def test_is_not_valid_state():
    for _ in range(10):
        assert not mqry.is_valid_state(gen_random_not_valid_str())


def test_get_actions():
    actions = mqry.get_actions()
    assert isinstance(actions, dict)
    assert len(actions) > 0


def test_is_valid_action():
    for action in mqry.get_actions():
        assert mqry.is_valid_action(action)


def test_is_not_valid_action():
    for _ in range(10):
        assert not mqry.is_valid_action(gen_random_not_valid_str())


def test_create_manuscript(temp_person):
    manu_id = mqry.create_manuscript(
        TEST_TITLE,
        TEST_AUTHOR_NAME,
        temp_person,
        TEST_REFEREE,
        mqry.SUBMITTED,
        TEST_TEXT,
        TEST_ABSTRACT,
    )
    object_id = ObjectId(manu_id)
    manuscript = mqry.dbc.read_one(mqry.MANU_COLLECT, {flds.ID: object_id})

    assert manuscript is not None
    assert manuscript[flds.TITLE] == TEST_TITLE
    assert manuscript[flds.AUTHOR] == TEST_AUTHOR_NAME
    assert manuscript[flds.AUTHOR_EMAIL] == temp_person
    assert manuscript[flds.REFEREES] == [TEST_REFEREE]
    assert manuscript[flds.STATE] == mqry.SUBMITTED
    assert manuscript[flds.TEXT] == TEST_TEXT
    assert manuscript[flds.ABSTRACT] == TEST_ABSTRACT
    assert isinstance(manuscript[flds.ID], str)

    delete_count = mqry.delete(manu_id)
    assert delete_count == 1
    assert mqry.dbc.read_one(mqry.MANU_COLLECT, {flds.ID: object_id}) is None


def test_update(temp_manu, temp_person):
    updated_id = mqry.update(
        temp_manu,
        "History of CS",
        "Andy Ng",
        temp_person,
        "some ref",
        mqry.REFEREE_REVIEW,
        "new text",
        "new abstract"
    )
    assert updated_id == temp_manu
    manuscript = mqry.get_one_manu(temp_manu)
    assert manuscript[flds.TITLE] == "History of CS"
    assert manuscript[flds.AUTHOR] == "Andy Ng"
    assert manuscript[flds.STATE] == mqry.REFEREE_REVIEW
    assert "some ref" in manuscript[flds.REFEREES]
    assert "new text" in manuscript[flds.TEXT]
    assert "new abstract" in manuscript[flds.ABSTRACT]


def test_delete(temp_manu):
    mqry.delete(temp_manu)
    assert not mqry.exists(temp_manu)


def test_get_manuscripts(temp_manu):
    manuscripts = mqry.get_manuscripts()
    assert isinstance(manuscripts, dict)
    assert len(manuscripts) > 0

    for _id, manuscript in manuscripts.items():
        assert isinstance(_id, str)
        assert isinstance(manuscript, dict)
        assert flds.ID in manuscript
        assert flds.TITLE in manuscript
        assert flds.AUTHOR in manuscript
        assert flds.AUTHOR_EMAIL in manuscript 
        assert flds.REFEREES in manuscript
        assert flds.STATE in manuscript
        assert flds.TEXT in manuscript
        if flds.ABSTRACT in manuscript:
         assert isinstance(manuscript[flds.ABSTRACT], str)
        # error outputs because some manuscripts extracted don't have abstract section from before
    assert temp_manu in manuscripts


def test_get_one_manu(temp_manu):
    assert mqry.get_one_manu(temp_manu) is not None


def test_exists(temp_manu):
    assert mqry.exists(temp_manu)


def test_doesnt_exist():
    assert not mqry.exists("nonexistent-id")


def test_handle_action_bad_state():
    with pytest.raises(ValueError):
        mqry.handle_action(gen_random_not_valid_str(), mqry.ACTIONS['ACCEPT'], manu=copy.deepcopy(mqry.SAMPLE_MANU), ref="ref")


def test_handle_action_bad_action():
    with pytest.raises(ValueError):
        mqry.handle_action(mqry.SUBMITTED, gen_random_not_valid_str(), manu=copy.deepcopy(mqry.SAMPLE_MANU), ref="ref")


def test_handle_action_valid_return():
    manu = copy.deepcopy(mqry.SAMPLE_MANU)
    for state in mqry.get_states():
        for action in mqry.get_actions():
            if state in mqry.STATE_TABLE and action in mqry.STATE_TABLE[state]:
                assert mqry.is_valid_state(mqry.handle_action(state, action, manu=manu, ref="r"))


def test_handle_action():
    manu = copy.deepcopy(mqry.SAMPLE_MANU)
    assert mqry.handle_action(mqry.SUBMITTED, mqry.ACTIONS['ASSIGN_REF'], manu=manu, ref="r") == mqry.REFEREE_REVIEW
    assert mqry.handle_action(mqry.SUBMITTED, mqry.ACTIONS['REJECT'], manu=manu) == mqry.REJECTED
    assert mqry.handle_action(mqry.REFEREE_REVIEW, mqry.ACTIONS['ACCEPT'], manu=manu) == mqry.COPY_EDIT
    assert mqry.handle_action(mqry.REFEREE_REVIEW, mqry.ACTIONS['ACCEPT_WITH_REV'], manu=manu) == mqry.AUTHOR_REVISION
    assert mqry.handle_action(mqry.AUTHOR_REVISION, mqry.ACTIONS['DONE'], manu=manu) == mqry.EDITOR_REVIEW
    assert mqry.handle_action(mqry.EDITOR_REVIEW, mqry.ACTIONS['ACCEPT'], manu=manu) == mqry.COPY_EDIT
    assert mqry.handle_action(mqry.COPY_EDIT, mqry.ACTIONS['DONE'], manu=manu) == mqry.AUTHOR_REVIEW
    assert mqry.handle_action(mqry.AUTHOR_REVIEW, mqry.ACTIONS['DONE'], manu=manu) == mqry.FORMATTING
    assert mqry.handle_action(mqry.FORMATTING, mqry.ACTIONS['DONE'], manu=manu) == mqry.PUBLISHED


def test_assign_ref(temp_manu):
    manu = mqry.get_one_manu(temp_manu)
    assert TEST_NEW_REFEREE not in manu[flds.REFEREES]
    mqry.assign_ref(manu, TEST_NEW_REFEREE)
    assert TEST_NEW_REFEREE in manu[flds.REFEREES]
    with pytest.raises(ValueError):
        mqry.assign_ref(manu, TEST_NEW_REFEREE)


def test_delete_ref(temp_manu):
    manu = mqry.get_one_manu(temp_manu)
    mqry.assign_ref(manu, TEST_NEW_REFEREE)
    mqry.delete_ref(manu, TEST_NEW_REFEREE)
    assert TEST_NEW_REFEREE not in manu[flds.REFEREES]
    with pytest.raises(ValueError):
        mqry.delete_ref(manu, TEST_NEW_REFEREE)


def test_get_active_manuscripts_editor(temp_person, temp_manu):
    person = ppl.read_one(temp_person)
    ppl.update(person[ppl.NAME], person[ppl.AFFILIATION], temp_person, [rls.ED_CODE])
    results = mqry.get_active_manuscripts(temp_person)
    assert temp_manu in [m[flds.ID] for m in results]


def test_get_active_manuscripts_author(temp_person, temp_manu):
    person = ppl.read_one(temp_person)
    ppl.update(person[ppl.NAME], person[ppl.AFFILIATION], temp_person, [rls.AUTHOR_CODE])
    results = mqry.get_active_manuscripts(temp_person)
    assert temp_manu in [m[flds.ID] for m in results]


def test_get_active_manuscripts_referee(temp_referee, temp_ref_manu):
    results = mqry.get_active_manuscripts(temp_referee)
    assert temp_ref_manu in [m[flds.ID] for m in results]


def test_can_choose_action_author(temp_person, temp_manu):
    manu = mqry.get_one_manu(temp_manu)
    manu[flds.STATE] = mqry.SUBMITTED

    person = ppl.read_one(temp_person)
    ppl.update(person[ppl.NAME], person[ppl.AFFILIATION], temp_person, [rls.AUTHOR_CODE])
    
    assert mqry.can_choose_action(temp_manu, temp_person) is True


def test_can_choose_action_referee(temp_person, temp_referee):
    manu_id = mqry.create_manuscript(
        "Test Ref Manu",
        "Author",
        temp_person,
        temp_referee,
        mqry.REFEREE_REVIEW,
        "Text",
        "Abstract"
    )
    try:
        assert mqry.can_choose_action(manu_id, temp_referee)
    finally:
        mqry.delete(manu_id)


def test_can_choose_action_editor(temp_person, temp_manu):
    person = ppl.read_one(temp_person)
    ppl.update(person[ppl.NAME], person[ppl.AFFILIATION], temp_person, [rls.ED_CODE])
    
    assert mqry.can_choose_action(temp_manu, temp_person) is True


def test_valid_actions_author_withdraw(temp_person):
    ppl.update("Author", "NYU", temp_person, [rls.AUTHOR_CODE])

    manu_id = mqry.create_manuscript(
        "Withdraw Test",
        "Author",
        temp_person,
        "",
        mqry.SUBMITTED,
        "Text",
        "Abstract"
    )

    try:
        actions = mqry.get_valid_actions(manu_id, temp_person)
        assert mqry.ACTIONS['WITHDRAW'] in actions
    finally:
        mqry.delete(manu_id)


def test_valid_actions_referee_submit_review(temp_person, temp_referee):
    ppl.update("Referee", "NYU", temp_referee, [rls.RE_CODE])

    manu_id = mqry.create_manuscript(
        "Ref Test",
        "Author X",
        temp_person,
        temp_referee,
        mqry.REFEREE_REVIEW,
        "Ref text",
        "Ref abstract"
    )

    try:
        actions = mqry.get_valid_actions(manu_id, temp_referee)
        assert mqry.ACTIONS['SUBMIT_REW'] in actions
    finally:
        mqry.delete(manu_id)


def test_valid_actions_editor_assign_ref(temp_person):
    author_email = "author1234@nyu.com"
    if not ppl.exists(author_email):
        ppl.create("Author Test", "NYU", author_email, [rls.AUTHOR_CODE])

    ppl.update("Editor", "NYU", temp_person, [rls.ED_CODE])

    manu_id = mqry.create_manuscript(
        "Editor Test",
        "Author Test",
        author_email,
        "",
        mqry.SUBMITTED,
        "Manu Text",
        "Abstract"
    )

    try:
        actions = mqry.get_valid_actions(manu_id, temp_person)
        assert mqry.ACTIONS['ASSIGN_REF'] in actions
    finally:
        mqry.delete(manu_id)
        ppl.delete(author_email)


