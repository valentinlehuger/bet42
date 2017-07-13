from betlib.mongo import insert, find_one
from bson import ObjectId
from betlib.utils import normalize
from team import find_team_by_name
from championship import find_championship

import time


def add_season(query):
	db_query = dict()

	assert query.get("championship", None)
	assert query.get("years", None)
	assert len(query["years"]) == 2
	assert query.get("games", None)

	db_query["championship"] = find_championship({"name": query["championship"]})
	if not db_query["championship"]:
		raise Exception("championship name not found")
	db_query["championship"] = db_query["championship"]["_id"]
	db_query["years"] = query["years"]

	db_query["games"] = dict()

	for day in query["games"]:
		print "======== %s journee =========" % (day)
		db_query["games"][day] = list()

		for game in query["games"][day]:
			print normalize(game["team_H"]), "-", normalize(game["team_A"])
			db_game = dict()
			db_game["team_H"] = find_team_by_name(normalize(game["team_H"]))["_id"]
			if not db_game["team_H"]:
				raise Exception("home team : %s not found" % game["team_H"])

			db_game["team_A"] = find_team_by_name(normalize(game["team_A"]))["_id"]
			if not db_game["team_A"]:
				raise Exception("away team : %s not found" % game["team_A"])

			db_game["date"] = game["date"]
			db_game["link"] = game["link"]
			db_game["score"] = {"score_H": game["score"]["score_H"], "score_A": game["score"]["score_A"]}

			game_id = insert(db_game, "prono", "games")
			db_query["games"][day].append(game_id)

	return insert(db_query ,"prono", "seasons")

def find_season(query):
	return find_one(query, "prono", "seasons")

def find_season_by_id(s_id):
	return find_season({"_id": ObjectId(s_id)})

def find_season_by_championship_years(championship, years):
	ch = find_championship({"name": championship})
	ch_id = ch.get("_id", "")

	return find_season({"championship": ObjectId(ch_id), "years": years})



