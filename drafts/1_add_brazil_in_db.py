from betlib.mongo import get_db
from betlib.models.game import find_games, update_game
import os
import json

clientMDB = get_db("prono")
# clientMDB = get_mongolab_db("prono")


#games_brasil_serie_a = [g for g in find_games({"link": {"$regex": "/brazil/serie-a"}})]
#games_brasil_serie_a_links = list(set([g["link"] for g in games_brasil_serie_a]))

#print len(games_brasil_serie_a)
#print len(games_brasil_serie_a_links)

json_path = "../data/crawl_soccerway_FR/games/"
for json_filename in os.listdir(json_path):
    if "updated" not in json_filename or "2015" not in json_filename:
        continue
    with open(json_path + json_filename) as json_file:
        print json_filename
        games = json.load(json_file)
        for game in games:
            if "game_link" in game and "/netherlands/eredivisie/" in game["game_link"]:
            # if "game_link" in game and "/brazil/serie-a" in game["game_link"]:

                if game["years"] is not None:
                    season = game["years"].split("/") if ("/" in game["years"]) else game["years"]
                else:
                    season = game["years"]


                if "half-time" in game["scores"]:
                    if "final" not in game["scores"]:
                        game["scores"]["final"] = game["scores"]["half-time"]
                        game["scores"]["half-time"] = " - "
                    score = {
                        "half_time": {
                            "home": game["scores"]["half-time"].split(" - ")[0],
                            "away": game["scores"]["half-time"].split(" - ")[1],
                        },
                        "final": {
                            "home": game["scores"].get("final", "").split(" - ")[0],
                            "away": game["scores"].get("final", " - ").split(" - ")[1],
                        }
                    }
                else:
                    score = {
                        "final": {
                            "home": game["scores"].get("final", "").split(" - ")[0],
                            "away": game["scores"].get("final", " - ").split(" - ")[1],
                        }
                    }

                ret = update_game({
                    "link": game["game_link"]
                    # "team_H": game["team_H"],
                    # "team_A": game["team_A"],
                }, {
                    "score": score,
                    "stadium": game["stadium"],
                    # "date": game["date"],
                    "region": game["country"],
                    # "division": game["division"],
                    "season": season
                }, clientMDB, verbose=True)
                if ret == "None":
                    print game["game_link"], "not found."
