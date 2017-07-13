from pymongo import MongoClient

def get_db(database, ip="localhost", port=27017):
	client = MongoClient(ip, port)
	return client[database] or None


def insert(query, db, collection):
	db = get_db(db)
	collection = db[collection]
	post_id = collection.insert(query)
	return post_id

def find_one(query, db, collection):
	db = get_db(db)
	collection = db[collection]
	return collection.find_one(query)
