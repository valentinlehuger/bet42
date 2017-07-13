from lxml import etree
import urllib2
import StringIO
import json



def get_resultat_from_season(season_number):
	print season_number
	link = "http://www.footballstats.fr/resultat-ligue1-%s.html" % season_number
	
	req = urllib2.Request(link)
	response = urllib2.urlopen(req)
	the_page = response.read()
	
	#### print the html	
	# print the_page

	parser = etree.HTMLParser()
	tree = etree.parse(StringIO.StringIO(the_page), parser=parser)
	root = tree.getroot()

	for node in root[1][1][3]:
		if etree.tostring(node).startswith("<center>\n<table class=\"sortable coupe\" border=\"1\""):
			resultats_node = node[0]



	## print the results part of html
	# print etree.tostring(resultats_node)


	ret = {}

	day = 0
	for index, sub_node in enumerate(resultats_node):
		if index > 0:
			if etree.tostring(sub_node).startswith('<tr class="titreintermediaire">'):
				day += 1
				# print index, "journee %s" % (index / 12 + 1)
				ret[str(day)] = list()
			elif etree.tostring(sub_node).startswith('<tr>\n                  </tr>'):
				continue
			else:
				# print index, sub_node[0].text, "-", sub_node[1].text, sub_node[2].text
				# print etree.tostring(sub_node)
				if sub_node[2].text is None:
					ret[str(day)].append([[sub_node[0].text, sub_node[1].text],[int(goal) for goal in sub_node[2][0].text.split('-')]])					
				else:
					ret[str(day)].append([[sub_node[0].text, sub_node[1].text],[int(goal) for goal in sub_node[2].text.split('-')]])
			# else :
			# 	print index
	return ret


# print get_resultat_from_season(2006)

ret = {}
for i in range(1947, 2015):
	ret[str(i)] = get_resultat_from_season(i)

with open('resultat_ligue_1.json', 'w') as f:
	json.dump(ret, f, sort_keys=True)




# , sort_keys=True, indent=2, separators=(',', ': '))


# return

# {
# 	# journee 1
# 	"1" : [
# 		# premier match
# 		[
# 			["team1", "team2"],	# equipes
# 			[3, 1]	#score
# 		],
# 	],
# }

