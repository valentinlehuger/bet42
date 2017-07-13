from betlib.models.game import find_games, update_game
from betlib.models.competition import find_competition_by_name, add_competition
from betlib.mongo import get_db, get_mongolab_db

# clientMDB = get_db("prono")
clientMDB = get_mongolab_db("prono")


def get_season_from_date(date):
    year = date[0:4]
    return [year, str(int(year) + 1)]


# compet = add_competition({"name": "primera division", "region": "argentina"})
compet = find_competition_by_name("primera division")
# compet = find_competition_by_name("brasileirao a")

# brazil_games = [g for g in find_games({"link":{"$regex": "/brazil/serie-a"}})]
brazil_games = [g for g in find_games({"link":{"$regex": "/argentina/primera-division"}})]


games_nb = len(brazil_games)
print games_nb

for game in brazil_games:
    new_game = {
        "division": compet["_id"],
        "season": get_season_from_date(game["date"])
    }

    update_game({"link": game["link"]}, new_game, clientMDB)

#    print game["division"]

#    print new_game
