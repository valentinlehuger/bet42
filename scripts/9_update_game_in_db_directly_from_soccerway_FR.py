from betlib.models.game import find_games, update_game
from betlib.mongo import get_db
from crawl_soccerway_FR import game_page
from datetime import datetime, timedelta
import sys
from bson import ObjectId

def update_game_in_db_from_soccerway():

    client = get_db("prono", mongolab=True)

    now = datetime.now() + timedelta(5)
    today = "%d_%02d_%02d" % (int(now.year), int(now.month), int(now.day))
    three_day_ago = datetime.now() - timedelta(5)
    today_minus_3_day = "%d_%02d_%02d" % (int(three_day_ago.year), int(three_day_ago.month), int(three_day_ago.day))
    print today_minus_3_day
    print today
    games = [g for g in  find_games({"date": {"$lte": today, "$gte":today_minus_3_day}}, connection=client)]
    # games = [g for g in  find_games({}, connection=client)] # all games

    print len(games)

    for game in games:
        if "link" in game:
            # print "http://fr.soccerway.com" + game["link"]
            if game["link"].startswith("http"):
                updated = game_page.get_page(game["link"])
            else:
                updated = game_page.get_page("http://fr.soccerway.com" + game["link"])
            # print updated.get("date", "")
            if updated is not None:
                if updated["scores"] is not None:
                    if "half-time" in updated["scores"]:
                        half_time = updated["scores"]["half-time"].split(" - ")
                        scores = {"half_time": {"home": half_time[0], "away": half_time[1]}}
                    else:
                        half_time = None
                        scores = dict()
                    if "final" in updated["scores"]:
                        final = updated["scores"]["final"].split(" - ")
                        scores["final"] = {"home": final[0], "away": final[1]}
                    else:
                        final = None
                        scores = None
                    if updated["years"] is not None:
                        updated["years"] = updated["years"].split("/")
                ret = update_game({"link": game["link"]}, {
                    "score": scores,
                    "stadium": updated["stadium"],
                    "region": updated["country"],
                    "start_time": updated["start_time"],
                    "season": updated["years"],
                    "date": updated.get("date", None),
                    "possession": updated.get("possession", None),
                    "corners": updated.get("corners", None),
                    "shots": updated.get("tirs", None),
                    "shots_on_target": updated.get("tirs_cadres", None),
                    "fouls": updated.get("fautes", None)
                }, verbose=True, connection=client)
                if ret is None:
                    print game["link"], "is up to date in db."
                else:
                    print "[success]", game["_id"]

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print "Usage: python 9_update_game_in_db_directly_from_soccerway_FR.py"
        sys.exit(-1)
    update_game_in_db_from_soccerway()
