from betlib.models.game import find_games, find_game
from bson import ObjectId
from betlib.mongo import get_db
# import sys

def last_seven_goals(game, last_games):
    """return the numbers of goals of the home and away team for the last seven matchs of home and away, numbers of goals of the 'current' team first"""

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]
    last_games_H = get_last_games_for_team(game["team_H"])
    last_games_A = get_last_games_for_team(game["team_A"])
    if len(last_games_H) < 7 or len(last_games_A) < 7:
        return None
    last_scores_H = list()
    for lgame in last_games_H:
        if (lgame["team_H"] == game["team_H"]):
            score_gameteam_H, score_adversary = int(lgame["score"]["final"]["home"]), int(lgame["score"]["final"]["away"])
        else:
            score_gameteam_H, score_adversary = int(lgame["score"]["final"]["away"]), int(lgame["score"]["final"]["home"])
        last_scores_H += [score_gameteam_H, score_adversary]
    last_scores_A = list()
    for lgame in last_games_A:
        if (lgame["team_H"] == game["team_A"]):
            score_gameteam_A, score_adversary = int(lgame["score"]["final"]["home"]), int(lgame["score"]["final"]["away"])
        else:
            score_gameteam_A, score_adversary = int(lgame["score"]["final"]["away"]), int(lgame["score"]["final"]["home"])
        last_scores_A += [score_gameteam_A, score_adversary]
    return last_scores_H[-7:] + last_scores_A[-7:]

def get_day(game, last_game):
    """ return the game day """

    day = 1
    for lgame in last_game:
        if lgame["date"] < game["date"] and (lgame["team_H"] == game["team_H"] or lgame["team_A"] == game["team_H"]):
            day += 1
    return [day]

def get_last_seven_results_home_pov(game, last_games):
    """ return last 7 results of home team and away team in a list """

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]

    last_games_H = get_last_games_for_team(game["team_H"])
    last_results_home = [(x["score"]["final"]["home"] + " - " + x["score"]["final"]["away"]) for x in last_games_H if len(last_games_H) >= 7]
    last_results_home = [1 if int(x.split(" - ")[0]) > int(x.split(" - ")[1]) else (-1 if int(x.split(" - ")[0]) < int(x.split(" - ")[1]) else 0) for x in last_results_home]

    last_games_A = get_last_games_for_team(game["team_A"])
    last_results_away = [(x["score"]["final"]["away"] + " - " + x["score"]["final"]["home"]) for x in last_games_A if len(last_games_A) >= 7]
    last_results_away = [1 if int(x.split(" - ")[0]) > int(x.split(" - ")[1]) else ( -1 if int(x.split(" - ")[0]) < int(x.split(" - ")[1]) else 0) for x in last_results_away]

    if len(last_results_home[-7:]) < 7 or len(last_results_away[-7:]) < 7:
        return None
    return last_results_home[-7:] + last_results_away[-7:]

def get_last_seven_results(game, last_games):
    """ return last 7 results of home team and away team in a list """

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]

    last_games_H = get_last_games_for_team(game["team_H"])
    last_results_home = [(x["score"]["final"]["home"] + " - " + x["score"]["final"]["away"]) if x["team_H"] == game["team_H"] else (x["score"]["final"]["away"] + " - " + x["score"]["final"]["home"]) for x in last_games_H if len(last_games_H) >= 7]
    last_results_home = [1 if int(x.split(" - ")[0]) > int(x.split(" - ")[1]) else ( -1 if int(x.split(" - ")[0]) < int(x.split(" - ")[1]) else 0) for x in last_results_home]

    last_games_A = get_last_games_for_team(game["team_A"])
    last_results_away = [(x["score"]["final"]["home"] + " - " + x["score"]["final"]["away"]) if x["team_H"] == game["team_A"] else (x["score"]["final"]["away"] + " - " + x["score"]["final"]["home"]) for x in last_games_A if len(last_games_A) >= 7]
    last_results_away = [1 if int(x.split(" - ")[0]) > int(x.split(" - ")[1]) else ( -1 if int(x.split(" - ")[0]) < int(x.split(" - ")[1]) else 0) for x in last_results_away]

    if len(last_results_home[-7:]) < 7 or len(last_results_away[-7:]) < 7:
        return None
    return last_results_home[-7:] + last_results_away[-7:]


def get_rankings(game, games, scale=False):
    """ returns ranking of home team and away team in a list """

    points = dict()
    for g in games:
        if g["team_H"] not in points:
            points[g["team_H"]] = 0
        if g["team_A"] not in points:
            points[g["team_A"]] = 0
        if int(g["score"]["final"]["home"]) > int(g["score"]["final"]["away"]):
            points[g["team_H"]] += 3
        elif int(g["score"]["final"]["home"]) < int(g["score"]["final"]["away"]):
            points[g["team_A"]] += 3
        else:
            points[g["team_H"]] += 1
            points[g["team_A"]] += 1
    if game["team_H"] not in points:
        points[game["team_H"]] = 0
    if game["team_A"] not in points:
        points[game["team_A"]] = 0
    rank_team_H = 1
    rank_team_A = 1
    for t in points:
        if points[t] > points[game["team_H"]] and t != game["team_H"]:
            rank_team_H += 1
        if points[t] > points[game["team_A"]] and t != game["team_A"]:
            rank_team_A += 1
    if scale:
        nb_teams = len(points)
        rank_team_H /= float(nb_teams)
        rank_team_A /= float(nb_teams)
    return [rank_team_H] + [rank_team_A]

def get_last_seven_ranking(game, last_games, scale=False):
    """ return the last seven ranking of home and away team in a list """

    def get_ranking_team(points_dict, team):
        """ return the ranking of team H and A in a tuple for a points dictionnary"""
        if team not in points_dict:
            points_dict[team] = 0
        rank_team = 1
        for t in points_dict:
            if points_dict[t] > points_dict[team] and t != team:
                rank_team += 1
        return rank_team

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]

    points = dict()
    last_games_id_h = [g["_id"] for g in get_last_games_for_team(game["team_H"])[-7:]]
    last_games_id_a = [g["_id"] for g in get_last_games_for_team(game["team_A"])[-7:]]

    if (len(last_games_id_h) < 7 or len(last_games_id_a) < 7):
        return None
    rankings_h = list()
    rankings_a = list()
    for lgame in last_games:
        # points update
        if lgame["team_H"] not in points:
            points[lgame["team_H"]] = 0
        if lgame["team_A"] not in points:
            points[lgame["team_A"]] = 0
        if int(lgame["score"]["final"]["home"]) > int(lgame["score"]["final"]["away"]):
            points[lgame["team_H"]] += 3
        elif int(lgame["score"]["final"]["home"]) < int(lgame["score"]["final"]["away"]):
            points[lgame["team_A"]] += 3
        else:
            points[lgame["team_H"]] += 1
            points[lgame["team_A"]] += 1
        if (lgame["_id"] in last_games_id_h):
            # calc rankings on points
            rank = get_ranking_team(points, game["team_H"])
            rankings_h.append(rank)
        if (lgame["_id"] in last_games_id_a):
            rank = get_ranking_team(points, game["team_A"])
            rankings_a.append(rank)

    if scale:
        nb_teams = len(points)
        print nb_teams
        print rankings_h
        rankings_h = [float(x) / nb_teams for x in rankings_h]
        rankings_a = [float(x) / nb_teams for x in rankings_a]
        print rankings_h
    return rankings_h + rankings_a



def get_last_seven_opponent_ranking(game, last_games, scale=False):
    """ return the last seven ranking of home and away team in a list """

    def get_ranking_team(points_dict, team):
        """ return the ranking of team H and A in a tuple for a points dictionnary"""
        if team not in points_dict:
            points_dict[team] = 0
        rank_team = 1
        for t in points_dict:
            if points_dict[t] > points_dict[team] and t != team:
                rank_team += 1
        return rank_team

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]

    points = dict()
    last_games_id_h = [g["_id"] for g in get_last_games_for_team(game["team_H"])[-7:]]
    last_games_id_a = [g["_id"] for g in get_last_games_for_team(game["team_A"])[-7:]]

    if (len(last_games_id_h) < 7 or len(last_games_id_a) < 7):
        return None
    rankings_h = list()
    rankings_a = list()
    for lgame in last_games:
        # points update
        if lgame["team_H"] not in points:
            points[lgame["team_H"]] = 0
        if lgame["team_A"] not in points:
            points[lgame["team_A"]] = 0
        if int(lgame["score"]["final"]["home"]) > int(lgame["score"]["final"]["away"]):
            points[lgame["team_H"]] += 3
        elif int(lgame["score"]["final"]["home"]) < int(lgame["score"]["final"]["away"]):
            points[lgame["team_A"]] += 3
        else:
            points[lgame["team_H"]] += 1
            points[lgame["team_A"]] += 1
        if (lgame["_id"] in last_games_id_h):
            # calc rankings on points
            if lgame["team_H"] == game["team_H"]:
                opponent_id = lgame["team_A"]
            else:
                opponent_id = lgame["team_H"]
            rank = get_ranking_team(points, opponent_id)
            rankings_h.append(rank)
        if (lgame["_id"] in last_games_id_a):
            if lgame["team_H"] == game["team_H"]:
                opponent_id = lgame["team_A"]
            else:
                opponent_id = lgame["team_H"]
            rank = get_ranking_team(points, opponent_id)
            rankings_a.append(rank)

    if scale:
        nb_teams = len(points)
        print nb_teams
        print rankings_h
        rankings_h = [float(x) / nb_teams for x in rankings_h]
        rankings_a = [float(x) / nb_teams for x in rankings_a]
        print rankings_h
    return rankings_h + rankings_a





def get_last_games_home_or_away(game, last_games):
    """ returns home or away of team home and away in a list """

    t_h = game["team_H"]
    t_a = game["team_A"]

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]

    last_games_H = get_last_games_for_team(t_h)[-7:]
    last_games_A = get_last_games_for_team(t_a)[-7:]

    if len(last_games_H) == 7 and len(last_games_A) == 7:
        return [(1 if g["team_H"] == t_h else 0) for g in last_games_H] + [(1 if g["team_H"] == t_a else 0) for g in last_games_A]
    else:
        return None


def get_last_games_shots(game, last_games):
    """ returns home or away of team home and away in a list """

    t_h = game["team_H"]
    t_a = game["team_A"]

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]

    last_games_H = get_last_games_for_team(t_h)[-7:]
    last_games_A = get_last_games_for_team(t_a)[-7:]

    if len(last_games_H) == 7 and len(last_games_A) == 7:
        return [(g["shots"]["home"] if g["team_H"] == t_h else g["shots"]["away"]) for g in last_games_H] + [(g["shots"]["home"] if g["team_H"] == t_a else g["shots"]["away"]) for g in last_games_A]
    else:
        return None


def get_last_games_goals_per_shots(game, last_games):
    """ returns home or away of team home and away in a list """

    t_h = game["team_H"]
    t_a = game["team_A"]

    def get_last_games_for_team(team):
        """ filter last games of one team """
        return [g for g in last_games if (g["team_H"] == team or g["team_A"] == team)]

    last_games_H = get_last_games_for_team(t_h)[-7:]
    last_games_A = get_last_games_for_team(t_a)[-7:]

    if len(last_games_H) == 7 and len(last_games_A) == 7:

        last_shots_h_tmp = [(float(g["shots"]["home"]) if g["team_H"] == t_h else float(g["shots"]["away"])) for g in last_games_H]
        last_goals_h = [(float(g["score"]["final"]["home"]) if g["team_H"] == t_h else float(g["score"]["final"]["away"])) for g in last_games_H]
        last_shots_h = [(1 if x == 0 else x) for x in last_shots_h_tmp]
        last_goals_per_shots_h = [str(x[0] / x[1]) for x in zip(last_goals_h, last_shots_h)]


        last_shots_a_tmp = [(float(g["shots"]["home"]) if g["team_H"] == t_a else float(g["shots"]["away"])) for g in last_games_A]
        last_goals_a = [(float(g["score"]["final"]["home"]) if g["team_H"] == t_a else float(g["score"]["final"]["away"])) for g in last_games_A]
        last_shots_a = [(1 if x == 0 else x) for x in last_shots_a_tmp]
        last_goals_per_shots_a = [str(x[0] / x[1]) for x in zip(last_goals_a, last_shots_a)]

        return last_goals_per_shots_h + last_goals_per_shots_a

    else:
        return None


def get_points(game, last_games):
    """ return the number of pints of the two teams """

    def get_points_for_team(team):
        points = 0
        for last_g in last_games:
            if last_g["team_H"] == team:
                if int(last_g["score"]["final"]["home"]) > int(last_g["score"]["final"]["away"]):
                    points += 3
                elif int(last_g["score"]["final"]["home"]) == int(last_g["score"]["final"]["away"]):
                    points += 1
            elif last_g["team_A"] == team:
                if int(last_g["score"]["final"]["home"]) < int(last_g["score"]["final"]["away"]):
                    points += 3
                if int(last_g["score"]["final"]["home"]) == int(last_g["score"]["final"]["away"]):
                    points += 1
        return str(points)

    points_h = get_points_for_team(game["team_H"])
    points_a = get_points_for_team(game["team_A"])

    return [points_h, points_a]


def construct_row(current_game, last_games, features):
    assert "ranking" in features
    constructor_funct = {
        "last_seven_results" : get_last_seven_results,
        "ranking" : get_rankings,
        "last_seven_results_home_pov" : get_last_seven_results_home_pov,
        "day" : get_day,
        "last_seven_home_or_away": get_last_games_home_or_away,
        "last_seven_goals" : last_seven_goals,
        "last_seven_shots": get_last_games_shots,
        "last_seven_goals_per_shots": get_last_games_goals_per_shots,
        "last_seven_rankings" : get_last_seven_ranking,
        "last_seven_opponents_rankings": get_last_seven_opponent_ranking,
        "points": get_points
    }
    line = list()

    for feature in features:
        f = constructor_funct[feature](current_game, last_games)
        if f is None:
            return None
        line += f
    result_current_game = 1 if int(current_game["score"]["final"]["home"]) > int(current_game["score"]["final"]["away"]) else (-1 if int(current_game["score"]["final"]["home"]) < int(current_game["score"]["final"]["away"]) else 0)
    line += [result_current_game]
    return line


def buildDataset(srcs, features, with_odds, mongolab=False):

    client = get_db("prono", mongolab=mongolab)

    game_issues = {-1 : [0, 0, 1],
                   0 : [0, 1, 0],
                   1 : [1, 0, 0]}
    # print srcs, features
    # print "=" * 30
    # sys.exit(-1)
    data_X_all = list()
    data_Y_all = list()
    odds_all = list()

    for competition_range in srcs:
        competition = competition_range[0]
        begin = competition_range[1]
        end = competition_range[2]

        for season in range(int(begin[0:4]), int(end[0:4])):
            if len(begin) == 4 and len(end) == 4:
                games = [g for g in find_games({"$query": {"division": ObjectId(competition), "season": [str(season), str(season + 1)]},  "$orderby": {"date": 1}}, connection=client)]
            else:
                games = [g for g in find_games({"$query": {"division": ObjectId(competition), "season": [str(season), str(season + 1)]}, "date" : {"$gte" : begin, "$lt" : end},  "$orderby": {"date": 1}}, connection=client)]
            for current_game in games:
                sub_games = [g for g in games if g["date"] < current_game["date"]]
                new_row = construct_row(current_game, sub_games, features)
                if new_row is None:
                    continue
                data_X_all.append(new_row[0:-1])
                data_Y_all.append(game_issues[new_row[-1]])
                if (with_odds is True):
                    odds_all.append([float(current_game["bets"]["bet365"]["home"]), float(current_game["bets"]["bet365"]["draw"]), float(current_game["bets"]["bet365"]["away"])])
                else:
                    odds_all.append(None)

    return data_X_all, data_Y_all, odds_all

def load_game_id_features(game_id, features, mongolab=False):

    client = get_db("prono", mongolab=mongolab)

    game = find_game({"$query": {"_id": ObjectId(game_id)}}, connection=client)
    constructor_funct = {
        "last_seven_results" : get_last_seven_results,
        "ranking" : get_rankings,
        "last_seven_results_home_pov" : get_last_seven_results_home_pov,
        "day" : get_day,
        "last_seven_home_or_away": get_last_games_home_or_away,
        "last_seven_goals" : last_seven_goals,
        "last_seven_shots": get_last_games_shots,
        "last_seven_goals_per_shots": get_last_games_goals_per_shots,
        "last_seven_rankings" : get_last_seven_ranking,
        "last_seven_opponents_rankings" : get_last_seven_opponent_ranking,
        "points": get_points
    }
    line = list()
    last_games = find_games({"$query": {"division": ObjectId(game["division"]), "season": [str(game["season"][0]), str(game["season"][1])],  "date": {"$lt": game["date"]}}}, connection=client)
    print game["date"]
    last_games = [l_g for l_g in last_games]
    for i, g in enumerate(last_games):
        if "final" not in g["score"]:
            last_games[i]["score"] = {"final": {"home": "2", "away": "2"}}
    for feature in features:
        f = constructor_funct[feature](game, last_games)
        if f is None:
            return None
        line += f
    # print line
    return line


if __name__ == '__main__':
    main()
