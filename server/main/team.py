from flask import render_template
from bson import ObjectId

from betlib.models.team import find_team_by_id
from betlib.models.game import find_games, remove_game, find_game_by_id, game_distinct

from . import main
from .. import client

@main.route("/team/<team_id>")
def team_page(team_id):
    team = find_team_by_id(ObjectId(team_id), connection=client)
    return render_template("team.html", team=team)

@main.route("/teams")
def teams_page():
    teams = [find_team_by_id(team_id, client) for team_id in game_distinct("team_A", client)]
    return render_template("teams.html", teams=teams)
