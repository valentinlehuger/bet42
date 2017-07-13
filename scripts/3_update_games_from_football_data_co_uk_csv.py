from betlib.models.team import find_team_by_name
from betlib.models.game import update_game
import csv
import os

corresponding_labels_table = {
    "Div": "division",
    "Date": "date",
    "HomeTeam": "team_H",
    "AwayTeam": "team_A",
    "FTHG": "full_time_home_team_goals",
    "FTAG": "full_time_away_team_goals",
    "FTR": "full_time_result",
    "HTHG": "half_time_home_team_goals",
    "HTAG": "half_time_away_team_goals",
    "HTR": "half_time_result",
    "Attendance": "crowd_attendance",
    "Referee": "referee",
    "HS": "home_team_shots",
    "AS": "away_team_shots",
    "HST": "home_team_shots_on_target",
    "AST": "away_team_shots_on_target",
    "HHW": "home_team_hit_woodwork",
    "AHW": "away_team_hit_woodwork",
    "HC": "home_team_corners",
    "AC": "away_team_corners",
    "HF": "home_team_fouls_committed",
    "AF": "away_team_fouls_committed",
    "HO": "home_team_offsides",
    "AO": "away_team_offsides",
    "HY": "home_team_yellow_cards",
    "AY": "away_team_yellow_cards",
    "HR": "home_team_red_cards",
    "AR": "away_team_red_cards",
    "HBP": "home_team_bookings_points",
    "ABP": "away_team_bookings_points",
    "B365H": "bet365_home_win_odds",
    "B365D": "bet365_draw_odds",
    "B365A": "bet365_away_win_odds"
}

with open(os.sys.argv[1], 'rb') as csvfile:
    games = list()
    csvreader = csv.reader(csvfile, delimiter=',')
    for i, line in enumerate(csvreader):
        if i == 0:
            labels = line
        else:
            games.append({corresponding_labels_table[labels[i]]:e for i, e in enumerate(line) if labels[i] in corresponding_labels_table})


    teams_unknown = set() ####################

    for i, g in enumerate(games):
        c_game = dict()
        query = dict()

        (day, month, year) = g["date"].split("/")
        query["date"] = "%s_%s_%s" % (("19" if int(year) > 60 else "20") + year, month, day)

        team_A = find_team_by_name(g["team_A"])
        if team_A == None:
            teams_unknown.add(g["team_A"])
        else:
            query["team_A"] = team_A["_id"]
        team_H = find_team_by_name(g["team_H"])
        if team_H == None:
            teams_unknown.add(g["team_H"])
        else:
            query["team_H"] = team_H["_id"]

        # print find_game(query)

        c_game = {
            "referee": g.get("referee", None),
            "crowd_attendance": g.get("crowd_attendance", None),
            "shots": {
                "home": g.get("home_team_shots", None),
                "away": g.get("away_team_shots", None)
            },
            "shots_on_target": {
                "home": g.get("home_team_shots_on_target", None),
                "away": g.get("away_team_shots_on_target", None)
            },
            "hit_woodwork": {
                "home": g.get("home_team_hit_woodwork", None),
                "away": g.get("away_team_hit_woodwork", None)
            },
            "corners": {
                "home": g.get("home_team_corners", None),
                "away": g.get("away_team_corners", None)
            },
            "fouls_committed": {
                "home": g.get("home_team_fouls_committed", None),
                "away": g.get("away_team_fouls_committed", None)
            },
            "offsides": {
                "home": g.get("home_team_offsides", None),
                "away": g.get("away_team_offsides", None)
            },
            "yellow_cards": {
                "home": g.get("home_team_yellow_cards", None),
                "away": g.get("away_team_yellow_cards", None)
            },
            "red_cards": {
                "home": g.get("home_team_red_cards", None),
                "away": g.get("away_team_red_cards", None)
            },
            "bets" : {
                "bet365": {
                    "home": g.get("bet365_home_win_odds", None),
                    "draw": g.get("bet365_draw_odds", None),
                    "away": g.get("bet365_away_win_odds", None)
                }
            }
        }

        # update_game(query, c_game)
        # print c_game

    print teams_unknown
    # print games[0]
    # for game in games:
    #     print games

    # datas = sorted([l for l in csvreader], key=itemgetter(0))
