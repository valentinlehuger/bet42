import os
import json
from betlib.models.game import add_game
from betlib.mongo import get_db


count = 0

path = os.sys.argv[1]
#for i, filename in enumerate(os.listdir(path)):

# db_connection = get_db("prono")
db_connection = get_db("prono")

for i, filename in enumerate(["calendar_2014_updated.json", "calendar_2015_updated.json"]):
    calendar = dict()
    with open(path + filename, "r") as f:
        calendar = json.load(f)
        f.close()
    for j, game_date in enumerate(calendar):
        for competition in calendar[game_date]:
            for g in calendar[game_date][competition]:
                if g["team_H"]["name"] is not None and g["team_A"]["name"] is not None:
                    if "/england/premier-league/" in g["game_link"]:
                    # if "/brazil/serie-a/" in g["game_link"]:
                        count += 1
                        print count
                        ret = add_game({
                            "team_H": g["team_H"],
                            "team_A": g["team_A"],
                            "link": g["game_link"],
                            "date": game_date
                        }, db_connection)
                        if ret == None:
                            print g["game_link"], " not added in DB."
