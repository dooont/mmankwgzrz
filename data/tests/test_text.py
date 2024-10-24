import data.text as txt


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    # check if each page is a str
    for key in texts:
        assert isinstance(key, str)