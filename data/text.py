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

def create():
    pass


def delete():
    pass


def update():
    pass


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
