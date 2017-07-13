from lxml import etree
import urllib2
import StringIO
import json

# for i in range(0, 100000):
# 	link = "http://www.francefootball.fr/ligue-1/2014-2015/resultats/n/8e-journee/%s" % i

# 	req = urllib2.Request(link)
# 	response = urllib2.urlopen(req)
# 	the_page = response.read()

# 	parser = etree.HTMLParser()
# 	tree = etree.parse(StringIO.StringIO(the_page), parser=parser)
# 	root = tree.getroot()

def get_day(num, day):
	link = "http://www.francefootball.fr/ligue-1/2014-2015/resultats/n/8e-journee/%s" % (num)
	req = urllib2.Request(link)
	response = urllib2.urlopen(req)
	the_page = response.read()

	parser = etree.HTMLParser()
	tree = etree.parse(StringIO.StringIO(the_page), parser=parser)
	root = tree.getroot()

	season = dict()


	if "<div class=\"ligneres\">" not in etree.tostring(root):
		return None

	print "  ========== Journee", day, "============  "

	days = list()

	date = dict()

	resultats = root[1][4][3][0][1][0][2][0]
	count = 0
	for node in list(resultats):
		if etree.tostring(node).startswith("<div class=\"ligneres\">"):
			for elem in node:
				if etree.tostring(elem).startswith("<div class=\"dateres\">"):
					date["hour"] = elem.text
				else:
					for elemment in elem:
						if etree.tostring(elemment).startswith("<div class=\"conteventres \">"):
							game = {
								"date": date,
								"team_H": elemment[0][0].text,
								"team_A": elemment[2][0].text,
								"score": {
									"score_H": elemment[1][0].text.split("-")[0],
									"score_A": elemment[1][0].text.split("-")[1],
								},
							"link": "http://www.francefootball.fr%s" % elemment[1][0].attrib["href"]
							}
							# print game
							days.append(game)
			count += 1
		elif etree.tostring(node).startswith("<div class=\"headres\"><div>"):
			date["date"] = node[0].text
	return days


#45209
# http://www.francefootball.fr/ligue-1/2013-2014/resultats/n/1ere-journee/45019
def crawl_ff_season(begin_nb, ligue="", years=[], days_nb=38, save_it=False):
	i = begin_nb
	season = dict()
	for day in range(i, i + days_nb):

		res = get_day(day, day - i + 1)
		if res is None:
			print day, None
		else:
			season[str(day - i + 1)] = res
			print len(res), "games"

	if save_it:
		with open('/Users/valentin/Projets/prono_foot/resources/%s_%s_%s.json' % (ligue, years[0], years[1]), 'w') as season_file:
			json.dump(season, season_file)
	return season
