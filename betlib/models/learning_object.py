from betlib.mongo import insert, find_one, find
from region import add_region
from bson import ObjectId

def add_learning_object(query, connection=None):
    assert query.get("name", None)

    if find_one({"name": query["name"]}, "prono", "learning_objects"):
        return "learning object named %s already exists" % (query["name"])

    return insert(query, "prono", "learning_objects", connection)

def find_learning_object(query, connection=None):
    return find_one(query, "prono", "learning_objects", connection)

def find_learning_object_by_name(name, connection=None):
    return find_competition({"name": name}, connection)

def find_learning_objects(query, connection=None):
    return find(query, "prono", "learning_objects", connection)

def find_learning_object_by_id(lo_id, connection=None):
    return find_one({"_id": ObjectId(lo_id)}, "prono", "learning_objects", connection)
