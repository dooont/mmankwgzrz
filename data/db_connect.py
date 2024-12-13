import os
from dotenv import load_dotenv
import pymongo as pm

load_dotenv()

LOCAL = "0"
CLOUD = "1"

JOURNAL_DB = 'journalDB'

client = None

MONGO_ID = '_id'


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print("Setting client because it is None.")
        if os.environ.get("CLOUD_MONGO", LOCAL) == CLOUD:
            mongo_uri = os.environ.get("MONGO_URI")
            if not mongo_uri:
                raise ValueError('You must set your MONGO_URI '
                                 + 'to use Mongo in the cloud.')
            print("Connecting to Mongo in the cloud.")
            client = pm.MongoClient(mongo_uri)
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()
    return client


def convert_mongo_id(doc: dict):
    """
    Converts MongoDB's ObjectId (_id) into a string so it can be serialized as
    JSON.
    """
    if MONGO_ID in doc:
        doc[MONGO_ID] = str(doc[MONGO_ID])


def create(collection: str, doc: dict, db=JOURNAL_DB):
    """
    Insert a single document into the specified collection in the database.
    """
    result = client[db][collection].insert_one(doc)
    return result


def read_one(collection: str, filt: dict, db=JOURNAL_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    doc = client[db][collection].find_one(filt)
    if doc:
        convert_mongo_id(doc)
    print(f"Document found: {doc}")
    return doc


def delete(collection: str, filt: dict, db=JOURNAL_DB):
    """
    Deletes the first document matching the filter.
    Returns the count of deleted documents.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


def delete_role(collection: str, filt: dict, role: str, db=JOURNAL_DB) -> bool:
    """
    Removes a specific role from a list in a document based on the filter.
    """
    print(f'{filt=}')
    result = client[db][collection].update_one(filt, {'$pull': role})
    return result.modified_count > 0  # True if a role was removed


def update(collection: str, filt: dict, update_dict: dict, db=JOURNAL_DB):
    """
    Updates fields in a document matching the filter with the provided updates.
    """
    return client[db][collection].update_one(filt, {'$set': update_dict})


def read(collection, db=JOURNAL_DB, no_id=True) -> list:
    """
    Retrieves all documents from the specified collection.
    """
    ret = []
    for doc in client[db][collection].find():
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=JOURNAL_DB, no_id=True) -> dict:
    """
    Retrieves all documents as a dictionary with the specified key as the
    dictionary key.
    """
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


def fetch_all_as_dict(key, collection, db=JOURNAL_DB):
    """
    Retrieves all documents as a dictionary with a specified field as the key.
    """
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret
