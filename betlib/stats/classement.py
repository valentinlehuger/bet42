from betlib.models.championship import find_championship
from betlib.models.season import find_season
from betlib.models.team import find_team_by_id
from betlib.models.game import find_game


def update_classement(day_games, classement, place):

    for day_game in day_games:

        game = find_game({"_id": day_game})
        team_H = find_team_by_id(game["team_H"])["name"]
        team_A = find_team_by_id(game["team_A"])["name"]

        if not classement.get(team_H, None):
            classement[team_H] = 0

        if not classement.get(team_A, None):
            classement[team_A] = 0

        if game["score"]["score_H"] > game["score"]["score_A"] and (place == "X" or place == "H"):
            classement[team_H] += 3
        elif game["score"]["score_H"] < game["score"]["score_A"] and (place == "X" or place == "A"):
            classement[team_A] += 3
        elif game["score"]["score_H"] == game["score"]["score_A"]:
            if place == "X" or place == "H":
                classement[team_H] += 1
            if place == "X" or place == "A":
                classement[team_A] += 1

    return classement

def get_classement(championship, years, day, place="X"):

    classement = dict()

    ch_id = find_championship({"name": championship})["_id"]
    if not ch_id:
        raise Exception("Championship %s not found" % (championship))

    season = find_season({"championship": ch_id, "years": years})
    if not season:
        raise Exception("Season %s %s not found" % (championship, years))

    for i in range(1, day + 1):
        classement = update_classement(season["games"][str(i)], classement, place)

    print classement
