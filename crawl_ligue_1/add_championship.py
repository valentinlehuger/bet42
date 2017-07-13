from mongo import insert, find_one
#from add_country import add_country


def add_championship(query):
    assert query.get("name", None)
    assert query.get("country", None)
    assert query.get("division", None)

    assert query["division"] >= 1
    assert query["division"] <= 9

    if find_one({"name": query["name"]}, "prono", "championships"):
        return "championship already exists"

    country_id = find_one({"name": query["country"]}, "prono", "countries")
    if country_id == None:
#        add_country({"name": query["country"]})
        country_id = find_one(query["country"], "prono", "countries")

    return insert({"name": query["name"], "country": country_id, "division": query["division"]}, "prono", "championships")
