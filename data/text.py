"""
This module interfaces to our text data.
"""

TITLE = 'title'
TEXT = 'text'
EMAIL = 'email'

TEST_KEY = 'HomePage'
SUBM_KEY = 'SubmissionsPage'
DEL_KEY = 'DeletePage'

text_dict = {
    TEST_KEY: {
        TITLE: 'Home Page',
        TEXT: 'This is a journal about building API servers.',
    },
    SUBM_KEY: {
        TITLE: 'Submissions Page',
        TEXT: 'All submissions must be original work in Word format.',
    },
    DEL_KEY: {
        TITLE: 'Delete Page',
        TEXT: 'This is a text to delete.',
    },
}


def create(page_key: str, title: str, text: str):
    new_page_key = page_key
    text_dict[new_page_key] = {
        TITLE: title,
        TEXT: text,
    }


def delete():
    pass


def update(page_key: str, title: str = None, text: str = None):
    if page_key in text_dict:
        if title:
            text_dict[page_key][TITLE] = title
        if text:
            text_dict[page_key][TEXT] = text


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    text = text_dict
    return text


def read_one(page_key: str):
    """
    Our contract:
        - Pass in a page key as argument.
        - Returns a dictionary for the page keyed on the page key.
    """
    result = text_dict.get(page_key, {})
    return result


def main():
    print(read())


if __name__ == '__main__':
    main()
