import os
import json
from betlib.models.game import update_game

path = os.sys.argv[1]
for i, filename in enumerate(os.listdir(path)):
    games = dict()
    with open(path + filename, "r") as f:
        print i, filename
        games = json.load(f)
        f.close()

    for j, game in enumerate(games):

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
            "division": game["division"],
            "season": season
        })
        if ret == "None":
            print game["game_link"], "not found."
