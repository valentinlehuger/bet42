from betlib.models.team import find_team_by_name
from betlib.models.championship import find_championship
from betlib.models.season import find_season
from betlib.models.game import find_game


def add_goals_scored(games, team):
	for game_id in games:
		game = find_game({"_id": game_id})

		if game["team_H"] == team:
			return int(game["score"]["score_H"])

		if game["team_A"] == team:
			return int(game["score"]["score_A"])
	return 0


def add_goals_against(games, team):
	for game_id in games:
		game = find_game({"_id": game_id})

		if game["team_H"] == team:
			return int(game["score"]["score_A"])

		if game["team_A"] == team:
			return int(game["score"]["score_H"])
	return 0


def average_goals_scored_per_game(championship, years, team, day):

	team_id = find_team_by_name(team)["_id"]
	c_id = find_championship({"name": championship})["_id"]
	season = find_season({"championship": c_id, "years": years})

	goals = 0

	i = 1

	for j in range(i, day + 1):
		goals += add_goals_scored(season["games"][str(j)], team_id)

	print "%s => %s goals scored in %s games => %s goals per game" % (team, goals, day, float(goals) / float(day))



def average_goals_against_per_game(championship, years, team, day):

	team_id = find_team_by_name(team)["_id"]
	c_id = find_championship({"name": championship})["_id"]
	season = find_season({"championship": c_id, "years": years})

	goals = 0

	i = 1

	for j in range(i, day + 1):
		goals += add_goals_against(season["games"][str(j)], team_id)

	print "%s => %s goals against in %s games => %s goals per game" % (team, goals, day, float(goals) / float(day))
