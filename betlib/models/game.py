# -*- coding: utf-8 -*-
from bson import ObjectId

from betlib.mongo import insert, find_one, find, update, update_multi, remove_one, distinct
from betlib.models.team import add_team, find_team_by_link
from betlib.models.stadium import find_stadium_by_name
from betlib.models.region import find_region_by_name
from betlib.utils import normalize
from crawl_soccerway_FR import get_correct_team_id

from crawl_soccerway_FR import game_page

import re

def add_game(query, connection=None):
    # print query
    new_game = dict()
    assert query.get("team_H")
    assert query.get("team_A")
    assert query.get("link")

    old_game = find_game_by_link(query["link"], connection)
    if old_game != None:
        print "game \"" + query["link"] + "\" already exists in DB."
        return None

    team_H = find_team_by_link(query["team_H"]["link"], connection)
    # print query["team_H"]["link"], team_H
    if not team_H:
        add_team(query["team_H"], verbose=False)
        team_H = find_team_by_link(query["team_H"]["link"], connection)
    if team_H is None:
        # print "OUT 1"
        return None
    new_game["team_H"] = get_correct_team_id(team_H["_id"], query["link"])

    team_A = find_team_by_link(query["team_A"]["link"], connection)
    if not team_A:
        add_team(query["team_A"], verbose=False)
        team_A = find_team_by_link(query["team_A"]["link"], connection)
    if team_A is None:
        # print "OUT 2"
        return None
    new_game["team_A"] = get_correct_team_id(team_A["_id"], query["link"])

    stadium = find_stadium_by_name(query.get("stadium", ""), connection)
    if stadium:
        new_game["stadium"] = stadium["_id"]

    region = find_region_by_name(query.get("region", ""), connection)
    if region:
        new_game["region"] = region["_id"]

    new_game["date"] = query.get("date", "")
    new_game["link"] = query.get("link", "")
    new_game["start_time"] = query.get("start_time", "")
    new_game["score"] = query.get("score", "")
    new_game["division"] = query.get("division", "")
    # print "new game =", new_game
    return insert(new_game, "prono", "games", connection)


def update_game(query, update_query, connection=None, verbose=False):
    new_query = {}
    game = find_game(query, connection)
    choice = "a"

    for field in update_query:
        if game is None or (field in game and game[field] != update_query[field] and update_query[field] is not None) or (field not in game):
            if verbose:
                while (choice not in "yYnN"):
                    if update_query[field] == str:
                        choice = raw_input("%s: Replace %s by %s? [Y/n]" % ((field + str(game["_id"]), normalize(game[field]), normalize(update_query[field]))))
                    else:
                        choice = 'Y'

                if choice == 'y' or choice == 'Y':
                    new_query[field] = update_query[field]
                elif choice == 'n' or choice == 'N':
                    continue
            else:
                new_query[field] = update_query[field]
    if len(new_query) > 0:
        return update(query, new_query, "prono", "games", connection)
    else:
        return None

def update_games(query, update_query):
    update_multi(query, update_query, "prono", "games")


def find_game(query, connection=None):
    return find_one(query, "prono", "games", connection)


def find_games(query, connection=None):
    return find(query, "prono", "games", connection)


def find_game_by_id(g_id, connection=None):
    return find_game({"_id": g_id}, connection=connection)


def find_game_by_link(link, connection=None):
    return find_game({"link": link}, connection)

def find_game_by_link_and_teams(link, team_H_id, team_A_id, connection=None):
    soccerway_id = re.findall("/(\d+)/", link)[-1]
    # print "=>", soccerway_id
    regex = re.compile("/{}/".format(soccerway_id))

    return [x for x in find_games({"link": {"$regex": regex}, "team_H": team_H_id, "team_A": team_A_id}, connection)]


def remove_game(query, connection=None):
    return remove_one(query, "prono", "games", connection)

def game_distinct(key, connection=None):
    return distinct(key, "prono", "games", connection)

def refresh_game(game_id, connection=None):
    game_origin = find_game({"_id": ObjectId(game_id)}, connection=connection)
    print game_origin
    if game_origin["link"]:
        updated = game_page.get_page("http://fr.soccerway.com" + game_origin["link"])
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
            ret = update_game({"link": game_origin["link"]}, {
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
            }, verbose=True, connection=connection)
            if ret is None:
                print "[NOTHING] game already in db. (%s)" % (game_id)
            else:
                print "[success]", game_id
            return ret
