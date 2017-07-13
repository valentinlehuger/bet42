from crawl_soccerway_FR import game_page
import sys
import json


for year in range(int(sys.argv[1]), int(sys.argv[2])):
    with open("../data/crawl_soccerway_FR/calendar/calendar_%d_updated.json" % year, "r") as f:
        calendar = json.load(f)
        f.close()

    games = list()
    i = 0
    for day in calendar:
        if str(year) in day:
            i += 1
#             if i <= 60:
#                 continue
            print year, i
            for competition in calendar[day]:
                for game in calendar[day][competition]:
                    g = game_page.get_page("http://fr.soccerway.com" + game["game_link"])
                    if g == None:
                        print "http://fr.soccerway.com" + game["game_link"]
                    else:
                        g.update(game)
                        games.append(g)
            if i % 60 == 0:
                with open("../data/crawl_soccerway_FR/games/%s_updated_%d.json" % ("games_" + str(year), i / 60), "w") as f:
                    print "save in ", "%s_updated_%d.json" % ("games_" + str(year), i / 60)
                    json.dump(games, f)
                    f.close()
                    games = list()
    with open("../data/crawl_soccerway_FR/games/%s_updated_%d.json" % ("games_" + str(year), (i / 60) + 1), "w") as f:
        print "save in ", "%s_updated_%d.json" % ("games_" + str(year), i / 60)
        json.dump(games, f)
        f.close()
        games = list()
