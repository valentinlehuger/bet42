from splinter import Browser
from splinter.exceptions import ElementDoesNotExist, DriverNotFoundError
from splinter.request_handler.status_code import HttpResponseError
from progressbar import Percentage, Bar, ETA, ProgressBar
import sys
import httplib
import json
import re

def error_print(origin, msg):
    print >> sys.stderr, origin, ": ", msg


def seasons_results_url_subcrawler(results_url):
    try:
        browser = Browser("phantomjs")
        browser.visit(results_url)
        seasons_table = browser.find_by_css("div.main-menu-gray")
        seasons_li = seasons_table.find_by_css("ul.main-filter").find_by_tag("li")
        seasons_url_dict = dict()
        for season in seasons_li:
            season_a = season.find_by_tag("a")
            season_year = season_a.text.split("/")[0]
            season_url = season_a["href"]
            if season_year is None or season_url is None:
                error_print("seasons results url subcrawler",
                            "anomaly in a season name or url")
                continue
            seasons_url_dict[season_year] = season_url
        del browser
        return seasons_url_dict
    except ElementDoesNotExist:
        error_print("seasons results url subcrawler",
                    "cannot find an element")
        del browser
        return None
    except HttpResponseError, e:
        error_print("seasons results url subcrawler",
                    results_url + ": " + e.msg)
        del browser
        return None


def results_pagination_subcrawler(results_page_url):
    try:
        browser = Browser("phantomjs")
        browser.visit(results_page_url)
        pagination = browser.find_by_id("pagination")
        if (len(pagination) > 1):
            error_print("results_pagination_subcrawler",
                        "warning: multiple pagination div, using first")
        pagination_elements_a = pagination.first.find_by_tag("a")
        pagination_url_list = list()
        for pe_a in pagination_elements_a[2:-2]:
            pagination_url_list.append(pe_a["href"])
        del browser
        return pagination_url_list
    except ElementDoesNotExist:
        del browser
        return None
    except HttpResponseError, e:
        error_print("results_pagination_subcrawler",
                    results_page_url + ": " + e.msg)
        del browser
        return None

def match_subcrawler(match_url=None):
    def trim_string(s):
        s = s.rstrip()
        s = s.lstrip()
        return re.sub(" +", " ", s)

    try:
        browser = Browser("phantomjs")
        browser.visit(match_url)
        match = dict()
        match["day"], match["date"], match["time"] = browser.find_by_css("p.datet").text.split(", ")
        match["day"] = trim_string(match["day"])
        match["date"] = trim_string(match["date"])
        match["time"] = trim_string(match["time"])
        participants = browser.find_by_id("col-content").find_by_tag("h1").text
        if " - " not in participants:
            error_print("match_subcrawler", "participant string malformat (miss ' - ')")
            return None
        match["team_H"], match["team_A"] = participants.split(" - ")
        match["score"] = dict()
        match["score"]["team_H"], match["score"]["team_A"] = browser.find_by_css("p.result").find_by_tag("strong").text.split(":")
        odds_aver = browser.find_by_css("tr.aver").find_by_css("td.right")
        if odds_aver.is_empty():
            error_print("match_subcrawler", "can't find odds for" + participants + match["date"])
            return match
        match["odd_H"] = odds_aver[0].text
        match["odd_D"] = odds_aver[1].text
        match["odd_A"] = odds_aver[2].text
        return match
    except HttpResponseError, e:
        error_print("match_subcrawler",
                    match_url + ": " + e.msg)
        return None


def results_page_subcrawler_fast(results_page_url):
    def parse_result_line(line):
        parse = dict()
        parse["time"] = line.find_by_css("td.table-time").text
        parse["team_H"], parse["team_A"] = line.find_by_css("td.table-participant").text.split(" - ")
        odds = line.find_by_css("td.odds-nowrp")
        parse["odd_H"] = odds[0].text
        parse["odd_D"] = odds[1].text
        parse["odd_A"] = odds[2].text
        return parse

    try:
        browser = Browser("phantomjs")
        browser.visit(results_page_url)
        results_table = browser.find_by_css("table.table-main")
        if results_table.is_empty():
            error_print("results_page_subcrawler", "no data found on" + browser.url)
            return None
        results_line = results_table.find_by_tag("tr")
        date = "NoFoundDate"
        results = dict()
        for line in results_line:
            if "deactivate" not in line["class"].split(" "):
                date_seeker = line.find_by_css("span.datet")
                if not date_seeker.is_empty():
                    date = date_seeker.text
                continue
            if date in results:
                results[date] = results[date] + [parse_result_line(line)]
            else:
                results[date] = [parse_result_line(line)]
        del browser
        return results
    except ElementDoesNotExist:
        del browser
        return None
    except HttpResponseError, e:
        error_print("results_page_subcrawler",
                    results_page_url + ": " + e.msg)
        del browser
        return None



def results_page_subcrawler(results_page_url):
    try:
        browser = Browser("phantomjs")
        browser.visit(results_page_url)
        results_table = browser.find_by_css("table.table-main")
        if results_table.is_empty():
            error_print("results_page_subcrawler", "no data found on" + browser.url)
            return None
        results_lines = browser.find_by_id("tournamentTable").find_by_id("tournamentTable").find_by_tag("tbody").find_by_css("tr.deactivate")
        results_url = [a["href"] for a in [line.find_by_tag("a") for line in results_lines]]
        del browser
        results = dict()
        for results_u in results_url:
            results_match = match_subcrawler(results_u)
            if results_match is None:
                continue
            if results_match["date"] in results:
                results[results_match["date"]] = results[results_match["date"]] + [results_match]
            else:
                results[results_match["date"]] = [results_match]
        del browser
        return results
    except ElementDoesNotExist:
        return None
    except HttpResponseError, e:
        error_print("results_page_subcrawler",
                    results_page_url + ": " + e.msg)
        return None


def season_subcrawler(season_url):
    def update_season_results(season_r, results_p):
        for date in results_p:
            if date in season_r:
                season_r[date] = season_r[date] + results_p[date]
            else:
                season_r[date] = results_p[date]
        return season_r

    try:
        print >> sys.stderr, "Crawling on", season_url
        results_pagination_list = results_pagination_subcrawler(season_url)
        if results_pagination_list is None:
            results_pagination_list = [season_url]
        else:
            results_pagination_list = [season_url] + results_pagination_list
        season_results = dict()
        # Progress bar init
        widgets_pb = [Percentage(), ' ', Bar(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets_pb, maxval=len(results_pagination_list))
        pbar.start()
        # / Progress bar init
        for idx, results_page_url in enumerate(results_pagination_list):
            results_page = results_page_subcrawler_fast(results_page_url)
            if results_page is not False:
                season_results = update_season_results(season_results, results_page)
            pbar.update(idx + 1)
        pbar.finish()
        return season_results
    except HttpResponseError, e:
        error_print("season_subcrawler",
                    season_url + ": " + e.msg)
        del browser
        return None


def results_crawler(results_url):
    try:
        seasons_dict = seasons_results_url_subcrawler(results_url)
        if seasons_dict is None:
            return None
        competition_results = dict()
        for season, season_url in seasons_dict.iteritems():
            season_results = season_subcrawler(season_url)
            if season_results is not False:
                competition_results[season] = season_results
        return competition_results
    except DriverNotFoundError:
        print >> sys.stderr, "Install phantomjs package"
        exit(-1)
    except HttpResponseError, e:
        print >> sys.stderr, results_url, ": ", e.msg
        return None


# instantiation base results adress list
results_pages = [
    "http://www.oddsportal.com/soccer/england/premier-league/results/",
    "http://www.oddsportal.com/soccer/france/ligue-1/results/",
    "http://www.oddsportal.com/soccer/spain/primera-division/results/",
    "http://www.oddsportal.com/soccer/germany/bundesliga/results/",
    "http://www.oddsportal.com/soccer/netherlands/eredivisie/results/"
]

results_dict = dict()
# for each results_adress
try:
    for results_p in results_pages:
        seasons_start_year_dict = results_crawler(results_p)
        if seasons_start_year_dict is not None:
            results_dict[results_p] = seasons_start_year_dict
    print json.dumps(results_dict)
except httplib.BadStatusLine:
    print json.dumps(results_dict)
    print >> sys.stderr, "You seen not connected to the interweb"
except KeyboardInterrupt:
    print json.dumps(results_dict)
    with open("/Users/valentin/Projets/prono_foot/crawl_oddportal/results.json", "w") as f:
        print "open file"
        json.dump(results_dict, f)
        print "close file"
        f.close()
    print >> sys.stderr, "KeyboardInterrupt"
