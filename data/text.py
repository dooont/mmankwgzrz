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
    if not key or not title or not text:
        raise ValueError("Key, title, and text must all be provided and "
                         "non-empty.")

    if dbc.read_one(TEXT_COLLECTION, {KEY: key}):
        raise ValueError(f"Key '{key}' already exists in the database.")

    doc = {KEY: key, TITLE: title, TEXT: text}
    dbc.create(TEXT_COLLECTION, doc)
    inserted_doc = dbc.read_one(TEXT_COLLECTION, {KEY: key})
    return dbc.convert_mongo_id(inserted_doc)


def delete(key: str) -> int:
    """
    Deletes a text entry from the database by key.
    """
    result = dbc.delete(TEXT_COLLECTION, {KEY: key})
    if result == 0:
        raise ValueError(f"No text entry found for key '{key}'.")
    return result


def update(key: str, title: str, text: str) -> dict:
    """
    Updates the title and/or text of an existing entry in the database.
    """
    if not key or not title or not text:
        raise ValueError("Key, title, and text must all be provided and "
                         "non-empty.")

    if not dbc.read_one(TEXT_COLLECTION, {KEY: key}):
        raise ValueError(f"No text entry found for key '{key}'.")

    dbc.update(TEXT_COLLECTION, {KEY: key}, {TITLE: title, TEXT: text})
    return dbc.read_one(TEXT_COLLECTION, {KEY: key})


def main():
    print("All entries:", read())


if __name__ == '__main__':
    main()
