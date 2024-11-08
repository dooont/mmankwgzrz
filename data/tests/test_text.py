import data.text as txt


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    # check if each page is a str
    for key in texts:
        assert isinstance(key, str)


def test_read_one():
    # check that TEST_KEY is being read properly
    assert len(txt.read_one(txt.TEST_KEY)) > 0


def test_read_one_not_found():
    # check that non-existent pages can't be read
    assert txt.read_one('Not a page key!') == {}


def test_create():
    # check that a new page can be created
    txt.create('NewPage', 'New Page', 'This is a new page.')
    assert txt.read_one('NewPage') == {'title': 'New Page', 
                                       'text': 'This is a new page.'}
