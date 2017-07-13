from betlib.mongo import insert, find_one, update
from bson import ObjectId


def add_stadium(query):
    assert query["name"]

    old = find_stadium_by_name(query["name"])
    if old is None:
        return insert(query, "prono", "stadiums")
    else:
        if old["name"] != query["name"]:
            print old["name"]
            print query["name"]
            print
        # print ret
    # print "%s already inserted" % (query["name"])
    return None


def find_stadium(query, connection=None):
    return find_one(query, "prono", "stadiums", connection)


def find_stadium_by_id(stadium_id):
    return find_stadium({"_id": ObjectId(stadium_id)})

def find_stadium_by_name(name, connection=None):
    return find_stadium({"$or": [{"name": name}, {"aliases": {"$in": [name]} }]}, connection)

def find_stadium_by_link(link):
    return find_stadium({"link": link})

def update_stadium(query, update_query, connection=None):
    return update(query, update_query, "prono", "stadiums", connection)

def add_stadium_alias(name, alias):
    if find_stadium_by_name(alias) == None:
        return update_stadium ({"name": name}, {"alias": alias})
