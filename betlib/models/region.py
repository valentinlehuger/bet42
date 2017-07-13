from betlib.mongo import insert, find_one, update
from bson import ObjectId


def add_region(query):
    assert query.get("name", None)
    return insert({"name": query["name"]}, "prono", "regions")

def find_region(query, connection=None):
    return find_one(query, "prono", "regions", connection)

def find_region_by_id(ct_id):
    return find_region({"_id": ObjectId(ct_id)})

def find_region_by_name(name, connection=None):
    return find_region({"$or": [{"name": name}, {"alias": {"$in": [name]}}]}, connection)

def update_region(query, update_query):
    return update(query, update_query, "prono", "regions")

def add_region_alias(name, alias):
    if find_region_by_name(alias) == None:
        return update_region ({"name": name}, {"alias": alias})
