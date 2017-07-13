from betlib.mongo import get_db
from betlib.models.game import find_games, update_game

client = get_db("prono", mongolab=True)

for game in find_games({}, client):
    if "link" in game:
        a = game["link"].split("?ICID=")
        if len(a) > 1:
            print game["link"]
            update_game(game, {"link": a[0]}, connection=client)


# db.games.ensureIndex({link: 1}, {unique:true, dropDups: true})
