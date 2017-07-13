from datetime import datetime, timedelta
from flask import render_template, redirect, url_for
from bson import ObjectId

from betlib.models.game import find_games, remove_game, find_game_by_id, game_distinct, refresh_game
from betlib.models.game import refresh_game as game_refresh_game
from betlib.models.competition import find_competition_by_id
from betlib.models.team import find_team_by_id
from betlib.models.learning_object import find_learning_objects

from betlib.prediction.pybrain import NN

from . import main
from .. import socketio, client

def get_last_3_day_games():
    now = datetime.now()
    today = "%d_%02d_%02d" % (int(now.year), int(now.month), int(now.day))
    three_day_ago = now - timedelta(7)
    today_minus_3_day = "%d_%02d_%02d" % (int(three_day_ago.year), int(three_day_ago.month), int(three_day_ago.day))
    games = [g for g in  find_games({"date": {"$lt": today, "$gte": today_minus_3_day}}, connection=client)]
    for i, game in enumerate(games):
        games[i]["team_H"] = find_team_by_id(game["team_H"], client)
        games[i]["team_A"] = find_team_by_id(game["team_A"], client)

    competitions_name = [(find_competition_by_id(div, client), div) for div in set([g["division"] for g in games])]
    # print competitions_name
    games_by_competitions = {str(div):{"name": k["name"], "games": []} for (k, div) in competitions_name if "name" in k}
    # print games_by_competitions

    for game in games:
        games_by_competitions[str(game["division"])]["games"].append(game)

    return games_by_competitions


def get_next_3_day_games():
    now = datetime.now()
    today = "%d_%02d_%02d" % (int(now.year), int(now.month), int(now.day))
    three_day_after = now + timedelta(7)
    today_plus_3_day = "%d_%02d_%02d" % (int(three_day_after.year), int(three_day_after.month), int(three_day_after.day))
    games = [g for g in  find_games({"date": {"$gte": today, "$lt": today_plus_3_day}}, connection=client)]

    for i, game in enumerate(games):
        games[i]["team_H"] = find_team_by_id(game["team_H"], client)
        games[i]["team_A"] = find_team_by_id(game["team_A"], client)

    competitions_name = [(find_competition_by_id(div, client), div) for div in set([g["division"] for g in games])]
    games_by_competitions = {str(div):{"name": k["name"], "games": []} for (k, div) in competitions_name if "name" in k}

    for game in games:
        games_by_competitions[str(game["division"])]["games"].append(game)

    return games_by_competitions


def formated_game(game_id):
    game = find_game_by_id(ObjectId(game_id), connection=client)
    team_H = find_team_by_id(ObjectId(game["team_H"]), connection=client)
    team_A = find_team_by_id(ObjectId(game["team_A"]), connection=client)
    division = find_competition_by_id(game["division"], connection=client)
    game["team_H"] = {"name": team_H["name"], "_id": team_H["_id"]}
    game["team_A"] = {"name": team_A["name"], "_id": team_A["_id"]}
    game["division"] = {"name": division["name"], "_id": division["_id"]}
    return game


@main.route("/game/<game_id>")
def game_page(game_id):
    game = formated_game(game_id)
    return render_template("game.html", game=game)


# @app.route("/removegame/<game_id>")
# def remove_one_game(game_id):
#     remove_game({"_id": ObjectId(game_id)}, connection=client)
#     return redirect(url_for('index'))

@socketio.on("refresh-game", namespace='/game')
def refresh_game(message):
    print game_refresh_game(message["game_id"], connection=client)

@socketio.on('get-nn-list', namespace='/game')
def get_nn_list():
    # print "Enter in get-nn-list"
    obj_list = [x for x in find_learning_objects({}, connection=client)]
    ret = list()
    for obj in obj_list:
        tmp = {}
        for k in obj:
            if k in ["name", "params"]:
                tmp[k] = obj[k]
        ret.append(tmp)
    socketio.emit('add-predict-obj', ret, namespace='/game')

@socketio.on('predict-game', namespace='/game')
def predict_game(datas):
    model = NN.NN()
    model.load_from_db(datas['name'])
    results = list([x for x in model.predict([datas['game']])])
    socketio.emit('add-prediction', {"name":datas['name'], 'home': str(results[0][0])[:5], 'X': str(results[0][1])[:5], 'away': str(results[0][2])[:5]}, namespace='/game')
