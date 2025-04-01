from pymongo import MongoClient

client = MongoClientclient = MongoClient("mongodb://127.0.0.1:27017/")
db = client['ecommerce_db']
books_collection = db['books']
author_collection = db["authors"]