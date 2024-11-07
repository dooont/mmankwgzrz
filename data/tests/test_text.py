import data.text as txt


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    # Check if each page key is a string
    for key in texts:
        assert isinstance(key, str)


def test_read_one():
    # Check that TEST_KEY is being read properly
    assert len(txt.read_one(txt.TEST_KEY)) > 0


def test_read_one_not_found():
    # Check that non-existent pages can't be read
    assert txt.read_one('Not a page key!') == {}


def test_create():
    new_key = 'NewPage'
    txt.create(new_key, 'New Page Title', 'This is a new page.')
    
    # Check that the new page has been added to the dictionary
    page = txt.read_one(new_key)
    assert page != {}
    assert page[txt.TITLE] == 'New Page Title'
    assert page[txt.TEXT] == 'This is a new page.'


def test_delete():
    key_to_delete = txt.TEST_KEY
    
    # Ensure the page exists before deletion
    assert txt.read_one(key_to_delete) != {}
    
    txt.delete(key_to_delete)
    assert txt.read_one(key_to_delete) == {}


def test_update():
    key_to_update = txt.SUBM_KEY
    
    # Ensure the page exists before update
    original_title = txt.read_one(key_to_update)[txt.TITLE]
    original_text = txt.read_one(key_to_update)[txt.TEXT]
    
    # Update the page
    txt.update(key_to_update, title="Updated Title", text="Updated text content.")
    
    # Check that the page was updated
    updated_page = txt.read_one(key_to_update)
    assert updated_page[txt.TITLE] == "Updated Title"
    assert updated_page[txt.TEXT] == "Updated text content."
    
    # Revert the changes for further testing
    txt.update(key_to_update, title=original_title, text=original_text)