#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ast import literal_eval
from lxml import etree
import urllib2
import StringIO
import re
import time

from betlib.utils import normalize

def get_left_main (node):
    for sub_node in node.iter("div"):
        if "class" in sub_node.attrib and "block_competition_left_tree-wrapper" in sub_node.attrib["class"].split(" "):
            return sub_node

def get_years_division (node):
    years = None
    division = None
    for sub_node in node.iter("li"):
        if "class" in sub_node.attrib and "current" in sub_node.attrib["class"].split(" "):
            current_li = sub_node
            for subn in current_li.iter("a"):
                if re.match(r'^\d{4}/\d{4}$', subn.text) != None:
                    years = subn.text
                else:
                    division = subn.text
    return years, division

def get_season (node):
    if node is None:
        return None
    left_main = get_left_main(node)
    try:
        country = left_main.find("h2").text
    except Exception:
        return None
    else:
        years, division = get_years_division(left_main)
    return country, years, division

def get_main_div (node):
    """ returns the main div from node in parameter """
    for sub_node in node.iter("div"):
        if "id" in sub_node.attrib and "yui-main" in sub_node.attrib["id"].split(" "):
            return sub_node

def get_date(n):
    """ returns date from node in parameter """
    for sub_node in n.iter("span"):
        if sub_node.text and re.match(r'^\d{1,2} .* \d{4}$', sub_node.text) != None:
            str_date = sub_node.text.split(" ")
            str_date[1] = {"janvier": "01", u"f\xe9vrier": "02", "mars": "03", "avril": "04", "mai": "05", "juin": "06", "juillet": "07", u'ao\xfbt': "08", "septembre": "09", "octobre": "10", "novembre": "11", u'd\xe9cembre': "12"}[str_date[1]]
            if len(str_date[0]) == 1:
                str_date[0] = "0" + str_date[0]
            return str_date[2] + "_" + str_date[1] + "_" + str_date[0]

    return None

def get_start_time(n):
    """ returns start_time from node in parameter """
    for sub_node in n.iter("span"):
        if sub_node.text and re.match(r"^\d{2}:\d{2}$", sub_node.text):
            return sub_node.text
    return None

def get_scores(n):
    """ return half-time and final scores from node in parameter """
    scores = dict()
    for sub_node in n.iter("dd"):
        if sub_node.text and re.match(r"^\d+ - \d+$", sub_node.text):
            if "half-time" in scores:
                scores["final"] = sub_node.text
                return scores
            else:
                scores["half-time"] = sub_node.text
    return scores

def get_stadium(node):
    """ returns stadium name from node in parameter """
    for sub_node in node.iter("dl"):
        if "Stade" in etree.tostring(sub_node):
            for sn in sub_node.iter("a"):
                return sn.text

def get_game_info(node):
    """ returns informations from node
        (date, start time, half-time score, final score, stadium)
    """
    ret = dict()
    date, start_time, scores, stadium = None, None, None, None
    if node is None:
        return None
    for sub_node in node.iter("div"):
        if "class" in sub_node.attrib:
            if "block_match_info-wrapper" in sub_node.attrib["class"].split(" "):
                # print etree.tostring(sub_node)
                date = get_date(sub_node)
                if date is not None:
                    ret["date"] = date
                ret["start_time"] = get_start_time(sub_node)
                ret["scores"] = get_scores(sub_node)
                ret["stadium"] = get_stadium(sub_node)
    return ret

def get_scorers(node):
    """ returns informations from node about scorers
    """
    goals = list()
    for sub_node in node.iter("div"):
        if "class" in sub_node.attrib:
            if "block_match_goals-wrapper" in sub_node.attrib["class"].split(" "):
                for sn in sub_node.iter("tr"):
                    player = {}
                    for ssn in sn.iter("td"):
                        if "class" in ssn.attrib and "event-icon" in ssn.attrib["class"].split(" "):
                            player["score"] = ssn[0].text
                        elif "class" in ssn.attrib and "player" in ssn.attrib["class"].split(" ") and len(ssn[0]) > 1:
                            if "player-a" in ssn.attrib["class"].split(" "):
                                player["name"] = ssn[0][0].text
                                player["id"] = ssn[0][0].attrib["href"]
                                player["time"] = ssn[0][1].text
                            else:
                                player["time"] = ssn[0][0].text
                                player["name"] = ssn[0][1].text
                                player["id"] = ssn[0][1].attrib["href"]
                    goals.append(player)
    return goals

def get_titular_and_trainer(node):
    players = list()
    trainer = None
    for i, sub_node in enumerate(node.iter("tr")):
        if i < 12 and "class" in sub_node.attrib and ("even" in sub_node.attrib["class"] or "odd" in sub_node.attrib["class"]):
            for sn in sub_node.iter("a"):
                players.append({
                    "name": sn.text,
                    "id": sn.attrib["href"]
                    })
        if i == 12:
            for sn in sub_node.iter("a"):
                trainer = {
                    "name":sn.text,
                    "id": sn.attrib["href"]
                }
    return players, trainer

def get_teams(node):
    """ returns informations from node about teams (composition, trainer, substitutes)
    """
    teams = dict()
    for sub_node in node.iter("div"):
        if "class" in sub_node.attrib:
            if "block_match_lineups-wrapper" in sub_node.attrib["class"]:
                for sn in sub_node.iter("div"):
                    if "class" in sn.attrib and "container" in sn.attrib["class"]:
                        if "left" in sn.attrib["class"]:
                            teams["home"] = dict()
                            teams["home"]["titulars"], teams["home"]["trainer"] = get_titular_and_trainer(sn)
                        if "right" in sn.attrib["class"]:
                            teams["away"] = dict()
                            teams["away"]["titulars"], teams["home"]["trainer"] = get_titular_and_trainer(sn)
            elif "block_match_substitutes-wrapper" in sub_node.attrib["class"]:
                for sn in sub_node.iter("div"):
                    if "class" in sn.attrib and "container" in sn.attrib["class"]:
                        if "left" in sn.attrib["class"]:
                            teams["home"]["substitutes"], _ = get_titular_and_trainer(sn)
                        if "right" in sn.attrib["class"]:
                            teams["away"]["substitutes"], _ = get_titular_and_trainer(sn)

    return teams


def get_possession(node):
    ret = dict()
    sub_node = etree.tostring([sn for sn in node.iter("script")][-1])
    sc = [x.strip() for x in [y for y in sub_node.split("\n")] if x.strip().startswith("chart.addSeries")][0]
    search = re.findall(r"[0-9]{1,2}", sc)
    if len(search) == 2:
        ret["home"] = search[0]
        ret["away"] = search[1]
    return ret

def get_stats_page(link, trytest=10):
    ret = dict()
    req = urllib2.Request(link)
    try:
        response = urllib2.urlopen(req, timeout=60)
        the_page = response.read()
    except Exception:
        if trytest > 0:
            print link, "retry in %d secs..." % (10 * (10 - trytest))
            time.sleep(10 * (10 - trytest))
            print "retry"
            return get_stats_page(link, trytest - 1)
        else:
            print "Fail to get page ", link
            return {}
    else:
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO.StringIO(the_page), parser=parser)
        root = tree.getroot()
        for node in root.iter("div"):
            if "class" in node.attrib and "chart_statsplus-wrapper" in node.attrib["class"]:
                for sub_node in node.iter("tr"):
                    if len(sub_node.getchildren()) == 3:
                        ret[normalize(unicode(sub_node[1].text)).lower().replace(" ", "_").replace("-", "_")] = {
                            "home": sub_node[0].text,
                            "away": sub_node[2].text
                        }
        ret.update({"possession": get_possession(root)})
    return ret

def get_stats(node):
    """ returns stats informations from node (corners, shots, possessions, shots on target, fouls, offsides) """
    stats = dict()
    for sub_node in node.iter("div"):
        if "class" in sub_node.attrib and "block_match_stats_plus_chart" in sub_node.attrib["class"]:
            for sn in sub_node.iter("iframe"):
                return get_stats_page("http://fr.soccerway.com" + sn.attrib["src"])
    return {}


def get_page(link, trytest=10):
    """returns all information about the game from the html link page in parameter"""

    req = urllib2.Request(link)
    try:
        response = urllib2.urlopen(req, timeout=60)
        the_page = response.read()
    except Exception:
        if trytest > 0:
            print link, "retry in %d secs..." % (10 * (10 - trytest))
            time.sleep(10 * (10 - trytest))
            print "retry"
            return get_page(link, trytest - 1)
        else:
            print "Fail to get page ", link
            return None
    else:
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO.StringIO(the_page), parser=parser)
        root = tree.getroot()
        main_div = get_main_div(root)
        if main_div is None:
            print "Fail to get page ", link
            return None

#        print etree.tostring(main_div)

        season = get_season(main_div)
        stats = get_stats(main_div)

        if season is not None:
            country, years, division = season
            game = {
                "game_link": link,
                "country": country,
                "years": years,
                "division": division,
            }
        else:
            game = {
                "game_link": link,
                "country": None,
                "years": None,
                "division": None,
            }
        game_infos = get_game_info(main_div)
        if game_infos is not None:
            game.update(game_infos)
        game.update({"scorers" : get_scorers(main_div)})
        game.update({"teams" : get_teams(main_div)})
        game.update(stats)
        return game


if __name__ == "__main__":
    print get_page("http://fr.soccerway.com/matches/2005/04/23/england/premier-league/everton-football-club/birmingham-city-fc/164709/?ICID=HP_MS_01_01")
    # print get_page("http://fr.soccerway.com/matches/2015/07/31/france/ligue-2/clermont-foot-auvergne/fc-sochaux-montbeliard/2045534/?ICID=PL_MS_05")["date"]
    # print get_page("http://fr.soccerway.com/matches/2015/05/23/france/ligue-1/olympique-de-marseille/sporting-club-de-bastia/1687447/?ICID=PL_MS_04")["date"]
    # print get_page("http://fr.soccerway.com/matches/2015/08/22/france/ligue-1/olympique-de-marseille/esperance-sportive-troyes-aube-champagne/2045854/")
    # print get_page("http://fr.soccerway.com/matches/2015/10/28/spain/primera-division/sociedad-deportiva-eibar/rayo-vallecano/2086354/")
# Informations to get

# country OK
# years OK
# Division OK
# date OK
# start time OK
# half-timne score OK
# final score OK
# stadium OK
# goals OK
    #player #time #id OK OK OK
# players OK
# trainers OK
# substitutes OK

# corners
# shots_on_target
# shots
# fouls
# offsides
# possession

# referees
