from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import MONGO_URI
from typing import Tuple


client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client.transactionDB
collection = db.transactions


def insert_transaction(transaction: dict) -> Tuple[bool, str]:
    """
    Вставляє транзакцію у колекцію.
    Повертає кортеж (True, inserted_id) при успіху або (False, error_message) при помилці.
    """
    try:
        result = collection.insert_one(transaction)
        return True, str(result.inserted_id)
    except Exception as e:
        return False, str(e)
