from betlib.models.game import find_games, update_games
from betlib.models.competition import find_competitions
import sys

if len(sys.argv) != 1:
    print "Usage : python 6...."
    sys.exit(-1)

competitions = [competition for competition in find_competitions({"$query": {}})]
for competition in competitions:
    update_games({"division": competition["name"]}, {"division": competition["_id"]})
