from betlib.models.competition import find_competition_by_id
from betlib.models.game import find_games, remove_game, find_game_by_id, game_distinct
from flask import render_template

from . import main
from .. import client

@main.route("/competitions")
def competitions_page():
    competitions = [find_competition_by_id(competition_id, client) for competition_id in game_distinct("division", client)]
    return render_template("competitions.html", competitions=competitions)
