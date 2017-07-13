# -*- coding: utf-8 -*-
from betlib.models.game import find_games
from betlib.mongo import get_db
from bson import ObjectId
import csv

client = get_db("prono", mongolab=True)


def flatten_game(game):
    new_game = dict()

    for field in game:
        if isinstance(game[field], dict):
            for sub_field in game[field]:
                if isinstance(game[field][sub_field], dict):
                    for last_sub_field in game[field][sub_field]:
                        new_game[".".join([field, sub_field, last_sub_field])] = game[field][sub_field][last_sub_field]
                else:
                    new_game[".".join([field, sub_field])] = game[field][sub_field]
        else:
            new_game[field] = game[field]

    return new_game


def export_season(division, years, fields=["_id", "team_H", "team_A", "date", "score.final.home", "score.final.away", "shots.home", "shots.away", "possession.home", "possession.away"]):
    season = [flatten_game(x) for x in find_games({"division": division, "season": years}, connection=client)]
    # print season[0]
    with open("data/seasons/" + "_".join([str(division), str(years[0]), str(years[1])]) + ".csv", "w") as f:

        for i, game in enumerate(season):
            if i == 0:
                f.write(";".join([unicode(field).encode('utf-8') for field in fields]) + "\n" )
            f.write(";".join([(unicode(game[field]).encode('utf-8') if field in game else str(None)) for field in fields]) + "\n" )
        f.close()


if __name__ == '__main__':

    # for division in ["55908dfe9734042e6bbd4360", "55908dfe9734042e6bbd435d", "55bb8325cd6e1b877323eb2e", "55908dfe9734042e6bbd435f", "55908dfe9734042e6bbd4359"]:
    #     for season in range(8):
    #         export_season(ObjectId(division), [str(2006 + season), str(2007 + season)])

    export_season(ObjectId("55908dfe9734042e6bbd4360"), ["2015", "2016"])
