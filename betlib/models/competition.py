from betlib.mongo import insert, find_one, find
from region import add_region
from bson import ObjectId

def add_competition(query):
    assert query.get("name", None)
    assert query.get("region", None)

    if find_one({"name": query["name"]}, "prono", "competitions"):
        return "competition already exists"

    region = find_one({"name": query["region"]}, "prono", "regions")
    if region == None:
        add_region({"name": query["region"]})
        region = find_one({"name": query["region"]}, "prono", "regions")

    region_id = region["_id"]

    return insert({"name": query["name"], "region": region_id}, "prono", "competitions")


def find_competition(query, connection=None):
    return find_one(query, "prono", "competitions", connection)

def find_competition_by_name(name, connection=None):
    return find_competition({"name": name}, connection)

def find_competitions(query):
    return find(query, "prono", "competitions")

def find_competition_by_id(ch_id, connection=None):
    return find_one({"_id": ObjectId(ch_id)}, "prono", "competitions", connection)
