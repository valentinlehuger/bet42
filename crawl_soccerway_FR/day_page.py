from lxml import etree
import urllib2
import StringIO
import time
import ast
import re


def get_first_node_by_tag_and_attr(node, tag, attr):
    for sub_node in node.iter(tag):
        if sub_node.attrib == attr:
            return sub_node

def get_team(node):
    try:
        link = node[0].attrib['href']
    except IndexError : link = None
    try:
        name = node[0].attrib['title']
    except IndexError : name = None
    return {"link" : link, "name" : name}

def get_game(node):
    team_H = get_team(node[1])
    try:
        score_link = node[2][0].attrib['href']
    except IndexError:
        score_link = None
    team_A = get_team(node[3])

    return {
        "team_H" : team_H,
        "game_link" : score_link,
        "team_A" : team_A
    }


def get_games_by_competition(node, tag, class_attr):
    ret = dict()
    for sub_node in node.iter(tag):
        if sub_node.attrib['class'] == class_attr:
            current_competition = sub_node[0][0][0].text
            ret[current_competition] = list()
        elif "match" in sub_node.attrib['class'].split(' '):
            ret[current_competition].append(get_game(sub_node))
    return ret

def get_competitions_not_loaded(node):
    competitions = dict()
    for sub_node in node.iter("tr"):
        if "class" in sub_node.attrib and "clickable" in sub_node.attrib["class"]:
            competitions[sub_node[0][0][0].text] = sub_node.attrib.get("id", "").replace("date_matches-", "")
    return competitions


def get_games_not_loaded(other_competitions, date):
    ret = dict()
    def get_team_nl(string):
        team = dict()
        m = re.search('href="(.*/)"', string)
        if m == None:
            return None
        team["link"] = m.groups()[0].replace("\\", "")
        m = re.search('title="(.*)"', string)
        if m == None:
            return None
        team["name"] = m.groups()[0].replace("\\", "")
        return team

    def get_game_link(string):
        m = re.search('href="(.*/)"', string)
        if m == None:
            return None
        return m.groups()[0].replace("\\", "")

    for competition in other_competitions:
        ret[competition] = list()
        _id = other_competitions[competition]
        url = 'http://fr.soccerway.com/a/block_date_matches?block_id=page_matches_1_block_date_matches_1&callback_params={"date":"%s"}&action=showMatches&params={"competition_id":%s}' % (date, _id)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        readed = response.read()
        string = ast.literal_eval(readed)["commands"][0]["parameters"]["content"]

        count = -1
        for x in string.split("<td"):
            if count >= 0 and count % 6 == 0:
                tmp = {}
            if count >= 0 and count % 6 == 2:
                tmp["game_link"] = get_game_link(x)

            if count >= 0 and count % 6 == 1:
                tmp["team_H"] = get_team_nl(x)
            if count >= 0 and count % 6 == 3:
                tmp["team_A"] = get_team_nl(x)
                if tmp["game_link"] is not None and tmp["team_H"] is not None and tmp["team_A"] is not None:
                    ret[competition].append(tmp)
            count += 1

    return ret

def get_page(year, month, day, trytest=10):
    link = "http://fr.soccerway.com/matches/%4d/%02d/%02d/" % (year, month, day)
    req = urllib2.Request(link)
    try:
        response = urllib2.urlopen(req, timeout=60)
        the_page = response.read()
    except urllib2.HTTPError:
        if trytest > 0 and ((day != 31 and month != 2) or (month == 2 and day < 29)):
            print year, month, day, "retry in 30 secs..."
            time.sleep(30)
            print "retry"
            return get_page(year, month, day, trytest - 1)
        else:
            print "Fail to get page ", year, month, day
            return None

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO.StringIO(the_page), parser=parser)
    root = tree.getroot()

    main_table = get_first_node_by_tag_and_attr(root, 'table', {'class': 'matches date_matches grouped '})

    games_link = get_games_by_competition(main_table, 'tr', 'group-head expanded loaded  ')
    other_competitions = get_competitions_not_loaded(main_table)
    date = "%4d-%02d-%02d" % (year, month, day)
    games_link.update(get_games_not_loaded(other_competitions, date))

    return games_link

if __name__ == "__main__":
    print get_page(2015, 06, 30)        #http://fr.soccerway.com/matches/2015/06/30/
    print get_page(2015, 02, 30)        #http://fr.soccerway.com/matches/2015/06/30/
    print get_page(2015, 04, 31)        #http://fr.soccerway.com/matches/2015/06/30/


# Use splinter to interact with the page
