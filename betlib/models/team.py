#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from betlib.mongo import insert, find_one, update, find
import betlib.mongo as bm
from bson import ObjectId


def add_team(query, verbose=False):
    assert query["name"]
    assert query["link"]

    if verbose:
        print "Do you want to add the team {\"name\": %s, \"link\": %s} [Y/n]:" % (query["name"], query["link"])

        while 42:
            line = os.sys.stdin.readline()
            line = line[:-1]
            if line in ["Y", "y", "yes"]:
                break
            elif line in ["N", "n", "no"]:
                return
            else:
                print "[Y/n]:"

    old = find_one({"link": query["link"]}, "prono", "teams")
    if old is None:
        print "added team :", query["name"]
        return insert(query, "prono", "teams")
    else:
        if old["name"] != query["name"]:
            print old["name"]
            print query["name"]
            print
        # print ret
    # print "%s already inserted" % (query["name"])
    return None


def find_team(query, connection=None):
    return find_one(query, "prono", "teams", connection)

def find_teams(query, connection=None):
    return find(query, "prono", "teams", connection)

def find_team_by_id(team_id, connection=None):
    return find_team({"_id": ObjectId(team_id)}, connection)

def find_team_by_name(name, connection=None):
    return find_team({"$or": [{"name": name}, {"aliases": {"$in": [name]} }]}, connection)

def find_team_by_link(link, connection=None):
    return find_team({"$or": [{"link": link}, {"link_aliases": {"$in": [link]} }]}, connection)

def update_team(query, update_query, connection=None):
    return update(query, update_query, "prono", "teams", connection)

def add_team_alias(name, alias, connection=None):
    team = find_team_by_name(name, connection)
    if team != None:
        if "aliases" not in team:
            team["aliases"] = list()
        # elif  alias in team["aliases"]:
        #     return None
        team["aliases"].append(alias)
        team["aliases"] = list(set(team["aliases"]))
        return update_team ({"name": name}, {"aliases": team["aliases"]}, connection)

def add_link_alias(link, link_alias):
    team = find_team_by_link(link)
    if team != None:
        if "link_aliases" not in team:
            team["link_aliases"] = list()
        team["link_aliases"].append(link_alias)
        return update_team({"link": link}, {"link_aliases": team["link_aliases"]})

def remove_team(query):
    return bm.remove_one(query, "prono", "teams")


if __name__ == "__main__":
    add_team({"name": "1", "link": "2"}, verbose=True)
