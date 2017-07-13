from betlib.models.game import find_games
import os

if len(os.sys.argv) != 4:
    print "Usage : python 5.... division year1 year2"
    print "Exemple : python 5.... \"Premier League\" 2010 2011"
    os.sys.exit(-1)

division = os.sys.argv[1]
years = [os.sys.argv[2], os.sys.argv[3]]

season = [game for game in find_games({"$query": {"season": years, "division": division}, "$orderby": {"date": 1}})]

ret = list()

ranking = {}

for game in season:

    if game["team_H"] not in ranking:
        ranking[game["team_H"]] = 0
    if game["team_A"] not in ranking:
        ranking[game["team_A"]] = 0

    if int(game["score"]["final"]["home"]) > int(game["score"]["final"]["away"]):
        ranking[game["team_H"]] += 3
    elif int(game["score"]["final"]["home"]) < int(game["score"]["final"]["away"]):
        ranking[game["team_A"]] += 3
    else:
        ranking[game["team_H"]] += 1
        ranking[game["team_A"]] += 1

    team_H = game["team_H"]
    team_A = game["team_A"]
    last_result_H = list()
    last_result_A = list()
    last_goals_on_shots_H = list()
    last_goals_on_shots_A = list()

    day = 1
    for last_game in season:
        if last_game["date"] < game["date"]:
            if team_H == last_game["team_H"]:
                day += 1
                last_result_H.append(last_game["score"]["final"]["home"] + " - " + last_game["score"]["final"]["away"])
                last_goals_on_shots_H.append(str(float(last_game["score"]["final"]["home"]) / float(last_game["shots"]["home"])))
            elif team_H == last_game["team_A"]:
                day += 1
                last_result_H.append(last_game["score"]["final"]["away"] + " - " + last_game["score"]["final"]["home"])
                last_goals_on_shots_H.append(str(float(last_game["score"]["final"]["away"]) / float(last_game["shots"]["away"])))
            if team_A == last_game["team_H"]:
                last_result_A.append(last_game["score"]["final"]["home"] + " - " + last_game["score"]["final"]["away"])
                last_goals_on_shots_A.append(str(float(last_game["score"]["final"]["home"]) / float(last_game["shots"]["home"])))
            elif team_A == last_game["team_A"]:
                last_result_A.append(last_game["score"]["final"]["away"] + " - " + last_game["score"]["final"]["home"])
                last_goals_on_shots_A.append(str(float(last_game["score"]["final"]["away"]) / float(last_game["shots"]["away"])))

    if len(last_result_H) >= 7 and len(last_result_A) >= 7:
        ret.append(last_result_H[-7:] + last_goals_on_shots_H[-7:] + [str(ranking[game["team_H"]])] + last_result_A[-7:] + last_goals_on_shots_A[-7:] + [str(ranking[game["team_A"]]), str(day), str(game["bets"]["bet365"]["home"]), str(game["bets"]["bet365"]["draw"]), str(game["bets"]["bet365"]["away"]), game["score"]["final"]["home"] + " - " + game["score"]["final"]["away"]])


def score_to_label(lst):
    labels = list()
    for e in lst:
        if "-" not in e:
            labels.append(e)
        else:
            a,b = [int(y) for y in e.split(" - ")]
            if a < b:
                labels.append(-1)
            elif a == b:
                labels.append(0)
            else:
                labels.append(1)
    return labels

for g in ret:
    if isinstance(g, list):
        print ",".join([str(x) for x in score_to_label(g)])
