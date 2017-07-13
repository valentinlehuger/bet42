from pymongo import MongoClient
from betlib import get_user_password

def get_db(database, ip="localhost", port=27017, mongolab=False):
    if mongolab:
        up = get_user_password()
        if up is None:
            print "Error to get db because file mongolab_register not define."
            return None
        else:
            return MongoClient('mongodb://' + up["user"] + ':' + up["password"] + '@ds055802.mongolab.com:55802/' + database)[database] or None
    else:
        client = MongoClient(ip, port)
        return client[database] or None

def insert(query, db, collection, connection=None):
    if connection is None:
        db = get_db(db)
    else:
        db = connection
    collection = db[collection]
    post_id = collection.insert(query)
    return post_id

def find_one(query, db, collection, connection=None):
    if connection is None:
        db = get_db(db)
    else:
        db = connection
    collection = db[collection]
    return collection.find_one(query)

def find(query, db, collection, connection=None):
    if connection is None:
        db = get_db(db)
    else:
        db = connection
    collection = db[collection]
    return collection.find(query)

def find_fields(query, fields, db, collection):
    db = get_db(db)
    collection = db[collection]
    return collection.find(query, fields)

def update(query, update_query, db, collection, connection=None):
    if connection is None:
        db = get_db(db)
    else:
        db = connection
    collection=db[collection]
    return collection.update(query, {"$set": update_query})

def update_multi(query, update_query, db, collection):
    db = get_db(db)
    collection=db[collection]
    return collection.update(query, {"$set": update_query}, multi=True)

def remove_one(query, db, collection, client=None):
	if not client:
		client = get_db(db)
	collection = client[collection]
	return collection.remove(query)

def distinct(key, db, collection, client=None):
	if not client:
		client = get_db(db)
	collection = client[collection]
	return collection.distinct(key)
