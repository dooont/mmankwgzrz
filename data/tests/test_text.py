import pytest
import data.text as txt


# Test Constants
TEST_KEY = 'TestPage'
TEST_TITLE = 'Test Title'
TEST_TEXT = 'This is a test text entry.'


@pytest.fixture(scope='function')
def temp_text():
    """
    Fixture to create a temporary text entry in the database for testing.
    Cleans up the entry after the test.
    """
    txt.create(TEST_KEY, TEST_TITLE, TEST_TEXT)
    yield TEST_KEY
    try:
        txt.delete(TEST_KEY)
    except:
        print('Text entry already deleted.')


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    assert len(texts) >= 0


def test_read_one(temp_text):
    entry = txt.read_one(temp_text)
    assert isinstance(entry, dict)
    assert entry[txt.KEY] == TEST_KEY
    assert entry[txt.TITLE] == TEST_TITLE
    assert entry[txt.TEXT] == TEST_TEXT


def test_read_one_not_found():
    result = txt.read_one('NonExistentKey')
    assert result == {}


def test_create():
    key = 'UniqueKey'
    title = 'Unique Title'
    text = 'This is unique content.'
    
    txt.create(key, title, text)
    entry = txt.read_one(key)
    assert entry[txt.KEY] == key
    assert entry[txt.TITLE] == title
    assert entry[txt.TEXT] == text

    # Clean up
    txt.delete(key)


def test_create_duplicate(temp_text):
    with pytest.raises(ValueError):
        txt.create(TEST_KEY, TEST_TITLE, TEST_TEXT)


def test_delete(temp_text):
    txt.delete(temp_text)
    result = txt.read_one(temp_text)
    assert result == {}


def test_delete_not_found():
    with pytest.raises(ValueError):
        txt.delete('NonExistentKey')


def test_update(temp_text):
    new_title = 'Updated Title'
    new_text = 'This is updated content.'

    txt.update(temp_text, title=new_title, text=new_text)
    entry = txt.read_one(temp_text)
    assert entry[txt.TITLE] == new_title
    assert entry[txt.TEXT] == new_text


def test_update_not_found():
    with pytest.raises(ValueError):
        txt.update('NonExistentKey', title='Should Fail', text='No Entry')
