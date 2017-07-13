from flask import Flask, render_template
from game import get_last_3_day_games, get_next_3_day_games
from betlib.models.learning_object import find_learning_objects
from betlib.models.competition import find_competition
from betlib.prediction.pybrain import NN

from bson import ObjectId
import ast

from . import main
from .. import socketio, client

@main.route('/')
def index():
    last_games = get_last_3_day_games()
    next_games = get_next_3_day_games()

    next_games_ids = {}

    for championship in next_games:
        next_games_ids[str(championship)] = []
        for game in next_games[championship]["games"]:
            print game
            next_games_ids[str(championship)].append(str(game["_id"]))

    # print last_games
    # print next_games
    if last_games is not None and next_games is not None:
        return render_template("index.html", params={"last_games": last_games, "next_games": next_games, "next_games_ids": next_games_ids})
    else:
        return render_template("index.html", params={})

@socketio.on('get-nn-list-championship', namespace='/index')
def get_nn_list_championship(championship_name):
    obj_list = [x for x in find_learning_objects({}, connection=client)]
    ret = list()
    for obj in obj_list:
        tmp = {}
        for k in obj:
            if k in ["name", "params"]:
                tmp[k] = obj[k]
        ret.append(tmp)
    print ret
    socketio.emit('add-predict-obj', {"list": ret, "championship": championship_name}, namespace='/index')


@socketio.on('predict-games', namespace='/index')
def predict_games(datas):

    print "Here"
    division = find_competition({"name": datas["championship"]}, connection=client)
    # print division
    games = [ObjectId(x) for x in ast.literal_eval(datas["games"].replace("&#39;", "\""))[str(division["_id"])]]
    # print games

    model = NN.NN()
    model.load_from_db(datas['name'])
    results = {str(games[i]):[str(a)[:5] for a in x] for i, x in enumerate(model.predict(games))}
    print results
    socketio.emit('add-predictions', results, namespace='/index')
