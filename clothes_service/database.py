from pymongo import MongoClient

client = MongoClientclient = MongoClient("mongodb://127.0.0.1:27017/")
db = client['ecommerce_db']
clothes_collection = db['clothes']
brands_collection = db["brands"]