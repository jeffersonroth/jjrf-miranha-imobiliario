"""MongoDB Utils."""

import sys
from pymongo import MongoClient

_COLLECTIONS = [
    "states",
    "cities",
    "houses"
]


def get_client() -> MongoClient:
    """Retrieves MongoDB client."""
    client = MongoClient('mongodb://root:password@mongo:27017/')
    return client


def create_database(name: str, client=get_client()) -> None:
    """Creates MongoDB database."""
    dblist = client.list_database_names()
    if name not in dblist:
        print(f"Creating MongoDB Database {name}", file=sys.stdout)
        client[name]


def create_collection(name: str, db: str, client=get_client()) -> None:
    """Creates MongoDB collection."""
    dblist = client.list_database_names()
    if db in dblist:
        database = client[db]
        collist = database.list_collection_names()
        if name not in collist:
            print(f"Creating MongoDB Collection {db}.{name}", file=sys.stdout)
            database[name]


def create_index_unique(field: str, db: str, coll: str, client=get_client()) -> None:
    """Creates Index for MongoDB collection."""
    dblist = client.list_database_names()
    if db in dblist:
        database = client[db]
        collist = database.list_collection_names()
        if coll in collist:
            collection = database[coll]
            print(f"Creating Index for MongoDB Collection {db}.{collection}")
            collection.create_index(field, unique=True)


def setup_db():
    """Setup MongoDB."""
    client = get_client()
    create_database(name="mcmakler", client=client)
    [create_collection(name=coll, db="mcmakler", client=client) for coll in _COLLECTIONS]
    [create_index_unique(field="url", db="mcmakler", coll=coll, client=client) for coll in _COLLECTIONS]


if __name__ == "__main__":
    setup_db()
