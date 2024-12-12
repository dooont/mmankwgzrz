"""
This module interfaces to our text data.
"""

import data.db_connect as dbc

# Fields
KEY = 'key'
TITLE = 'title'
TEXT = 'text'

TEXT_COLLECTION = 'text'

client = dbc.connect_db()


def read() -> dict:
    """
    Reads all text entries from the database and returns them as a dictionary.
    """
    return dbc.read_dict(TEXT_COLLECTION, KEY)


def read_one(key: str) -> dict:
    """
    Reads a single text entry by key.
    """
    result = dbc.read_one(TEXT_COLLECTION, {KEY: key})
    if not result:
        return {}
    return result


def create(key: str, title: str, text: str) -> dict:
    """
    Creates a new text entry in the database.
    """
    existing = dbc.read_one(TEXT_COLLECTION, {KEY: key})

    if existing:
        raise ValueError(f"Key '{key}' already exists in the database.")

    doc = {KEY: key, TITLE: title, TEXT: text}
    dbc.create(TEXT_COLLECTION, doc)
    return doc


def delete(key: str) -> int:
    """
    Deletes a text entry from the database by key.
    """
    result = dbc.delete(TEXT_COLLECTION, {KEY: key})
    if result == 0:
        raise ValueError(f"No text entry found for key '{key}'.")
    return result


def update(key: str, title: str = None, text: str = None) -> dict:
    """
    Updates the title and/or text of an existing entry in the database.
    """
    update_dict = {}
    if title is not None:
        update_dict[TITLE] = title
    if text is not None:
        update_dict[TEXT] = text

    if not update_dict:
        raise ValueError("No fields provided for update.")

    result = dbc.update(TEXT_COLLECTION, {KEY: key}, update_dict)
    if result.matched_count == 0:
        raise ValueError(f"No text entry found for key '{key}'.")
    return result


def main():
    print("All entries:", read())


if __name__ == '__main__':
    main()
