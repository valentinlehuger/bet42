from betlib.mongo import insert, find_one, update
from bson import ObjectId


def add_people(query):
    assert query.get("name", None)
    assert query.get("link", None)
    old = find_people_by_link(query["link"])
    if old == None:
        return insert({"name": query["name"], "link": query["link"]}, "prono", "peoples")
    elif old["name"] != query["name"]:
        print query["name"], "is already existing with this name :"
        return add_people_alias(old["name"], query["name"])
    else:
        return None

def find_people(query):
    return find_one(query, "prono", "peoples")

def find_people_by_id(ct_id):
    return find_people({"_id": ObjectId(ct_id)})

def find_people_by_name(name):
    return find_people({"$or": [{"name": name}, {"alias": {"$in": [name]}}]})

def find_people_by_link(link):
    return find_people({"link": link})

def update_people(query, update_query):
    return update(query, update_query, "prono", "peoples")

def add_people_alias(name, alias):
    if find_people_by_name(alias) == None:
        return update_people ({"name": name}, {"alias": alias})
