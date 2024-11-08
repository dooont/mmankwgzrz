import pytest
import data.text as txt


@pytest.fixture(scope='function')
def temp_text():
    temp_key = 'TempPage'
    txt.create(temp_key, 'Temp Page Title', 'This is a temp page.')
    yield temp_key
    txt.delete(temp_key)


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    # Check if each page key is a string
    for key in texts:
        assert isinstance(key, str)


def test_read_one(temp_text):
    # Check that TEST_KEY is being read properly
    assert len(txt.read_one(temp_text)) > 0


def test_read_one_not_found():
    # Check that non-existent pages can't be read
    assert txt.read_one('Not a page key!') == {}


def test_create(temp_text):
    new_key = temp_text
    page = txt.read_one(temp_text)
    assert page != {}
    assert page[txt.TITLE] == 'Temp Page Title'
    assert page[txt.TEXT] == 'This is a temp page.'


def test_delete(temp_text):
    assert txt.read_one(temp_text) != {}
    txt.delete(temp_text)
    assert txt.read_one(temp_text) == {}


@pytest.fixture(scope='function')
def setup_update():
    key_to_update = txt.SUBM_KEY
    original_data = txt.read_one(key_to_update)
    yield key_to_update
    txt.update(key_to_update, title=original_data[txt.TITLE], text=original_data[txt.TEXT])


def test_update(setup_update):
    key_to_update = setup_update
    
    original_data = txt.read_one(key_to_update)
    original_title = original_data[txt.TITLE]
    original_text = original_data[txt.TEXT]

    txt.update(key_to_update, title="Updated Title", text="Updated text content.")

    updated_page = txt.read_one(key_to_update)
    assert updated_page[txt.TITLE] == "Updated Title"
    assert updated_page[txt.TEXT] == "Updated text content."
    