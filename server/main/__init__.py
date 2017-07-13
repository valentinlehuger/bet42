from flask import Blueprint

main = Blueprint('main', __name__)

import index, competition, game, team
