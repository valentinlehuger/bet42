from betlib.models.team import find_team_by_name
from betlib.models.championship import find_championship
from betlib.models.season import find_season
from betlib.models.game import find_game

def get_result(games, team):

	for game_id in games:
		game = find_game({"_id": game_id})

		if game["team_H"] == team:
			if game["score"]["score_H"] == game["score"]["score_A"]:
				return "N"

			elif game["score"]["score_H"] > game["score"]["score_A"]:
				return "V"
			
			else:
				return "D"


		if game["team_A"] == team:
			if game["score"]["score_H"] == game["score"]["score_A"]:
				return "N"

			elif game["score"]["score_H"] > game["score"]["score_A"]:
				return "D"

			else:
				return "V"

	print "NADA"
	return ""


def get_last_games(championship, years, team, day, nb_days=5):

	team_id = find_team_by_name(team)["_id"]
	c_id = find_championship({"name": championship})["_id"]
	season = find_season({"championship": c_id, "years": years})

	last_games = list()

	i = day - nb_days
	if i < 1:
		i = 1

	for j in range(i + 1, i + nb_days + 1):
		last_games.append(get_result(season["games"][str(j)], team_id))

	print last_games
