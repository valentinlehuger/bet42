from betlib.models.game import find_game_by_link_and_teams, add_game
from betlib.models.team import find_team_by_link
from betlib.models.competition import find_competition_by_name
from datetime import datetime, timedelta
from betlib.mongo import get_db
from bson import ObjectId
# from betlib.utils import normalize

from crawl_soccerway_FR.day_page import get_page as dp_get_page
from crawl_soccerway_FR.game_page import get_page as gp_get_page

client = get_db("prono", mongolab=True)

delta = 5
authorized_comps = [
    "France - Ligue 1",
    "England - Premier League",
    "Germany - Bundesliga",
    u'Spain - Primera Divisi\xf3n',
    "Netherlands - Eredevisie"
]

mapping_comps = {
    "Ligue 1": ObjectId("55908dfe9734042e6bbd4360"), # Ligue 1
    "Liga BBVA": ObjectId("55bb8325cd6e1b877323eb2e"), # Spain - primera division
    "Premier League": ObjectId("55908dfe9734042e6bbd4359"), # Premier League
    "Bundesliga": ObjectId("55908dfe9734042e6bbd435f"), # Bundesliga
    "Eredivisie": ObjectId("55908dfe9734042e6bbd435d") # Eredevisie
}

now = datetime.now()

games = {}
count = 0
for i in range(delta):
    current = now + timedelta(i + 1)
    current_str = "%d_%02d_%02d" % (int(current.year), int(current.month), int(current.day))

    print current_str

    games[current_str] = dp_get_page(int(current.year), int(current.month), int(current.day))
    # print [x for x in games[current_str] if "Spain" in x]
    count += len(games[current_str])

print "Get {} games from {} to {}.".format(count, min(games), max(games))




authorized = dict()
others = dict()
count = 0
for date in games:
    for comp in games[date]:
        if comp in authorized_comps:
            authorized[comp] = list()
            for game in games[date][comp]:
                team_H = find_team_by_link(game["team_H"]["link"], client)
                team_A = find_team_by_link(game["team_A"]["link"], client)
                if team_H == None:
                    print "H none", game["game_link"]
                elif team_A == None:
                    print "A none", game["game_link"]
                elif find_game_by_link_and_teams(game["game_link"], team_H["_id"], team_A["_id"], client) == []:
                    game = gp_get_page("http://fr.soccerway.com" + game["game_link"])
                    authorized[comp].append(game)
                    db_game = {
                        "team_H": team_H,
                        "team_A": team_A,
                        "link": game["game_link"],
                        "date": date,
                        "division": mapping_comps[game["division"]]
                    }
                    
                    add_game(db_game, client)
                    count += 1

print "Get {} games added to db.".format(count)
