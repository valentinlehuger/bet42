from splinter import Browser

browser = Browser('phantomjs')
browser.visit("http://www.oddsportal.com/soccer/england/premier-league-2003-2004/results/#/page/1/")
games = browser.find_by_id("tournamentTable").find_by_id("tournamentTable").find_by_tag("tbody").find_by_css("tr.deactivate")
for game in games:
    if "deactivate" not in game["class"].split(" "):
        print "skip"
        continue
    time = game.find_by_css("td.table-time").text
    match = game.find_by_css("td.table-participant").text
    if len(game.find_by_css("td.table-participant").find_by_tag("a").find_by_tag("span")) > 0:
        winning_team = game.find_by_css("td.table-participant").find_by_tag("a").find_by_tag("span").text
    else:
        winning_team = "DRAW"
    odds = game.find_by_css("td.odds-nowrp")
    odd_H = odds[0].text
    odd_D = odds[1].text
    odd_A = odds[2].text
    link = game.find_by_css("td.table-participant").find_by_tag("a")["href"]
    # link = ""
    print match + " @" + time + " --> " + odd_H + " " + odd_D + " " + odd_A + " --> " + winning_team + " " + link

print "=" * 80
print "=" * 80
print "=" * 80
del browser
browser = Browser('phantomjs')
browser.visit("http://www.oddsportal.com/soccer/england/premier-league-2003-2004/results/#/page/2/")
games = browser.find_by_id("tournamentTable").find_by_id("tournamentTable").find_by_tag("tbody").find_by_css("tr.deactivate")
for game in games:
    if "deactivate" not in game["class"].split(" "):
        print "skip"
        continue
    time = game.find_by_css("td.table-time").text
    match = game.find_by_css("td.table-participant").text
    if len(game.find_by_css("td.table-participant").find_by_tag("a").find_by_tag("span")) > 0:
        winning_team = game.find_by_css("td.table-participant").find_by_tag("a").find_by_tag("span").text
    else:
        winning_team = "DRAW"
    odds = game.find_by_css("td.odds-nowrp")
    odd_H = odds[0].text
    odd_D = odds[1].text
    odd_A = odds[2].text
    link = game.find_by_css("td.table-participant").find_by_tag("a")["href"]
    # link = ""
    print match + " @" + time + " --> " + odd_H + " " + odd_D + " " + odd_A + " --> " + winning_team + " " + link
del browser
