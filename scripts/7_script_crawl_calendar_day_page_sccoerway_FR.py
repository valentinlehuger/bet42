from crawl_soccerway_FR import day_page
import sys
import json

for year in range(int(sys.argv[1]), int(sys.argv[1]) + 1):
    games_calendar = dict()
    for month in range(1, 13):
        print year, month
        for day in range(1, 32):
            games_day = day_page.get_page(year, month, day)
            if games_day != None:
                games_calendar["%4d_%02d_%02d" % (year, month, day)] = games_day
            if month == 12 and day == 31:
                with open("../data/crawl_soccerway_FR/calendar/%s_updated.json" % "calendar_%d" % year, "w") as f:
                    print "save year %d" % year
                    json.dump(games_calendar, f)
                    f.close()
