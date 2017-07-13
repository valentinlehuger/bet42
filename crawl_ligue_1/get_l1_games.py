import json
from add_championship import add_championship

with open("resultat_ligue_1.json", "r") as ligue1_file:
	l1_file = json.load(ligue1_file)


championship = dict()
championship["name"] = "ligue_1"
championship["country"] = "france"
championship["division"] = 1
print "championship = ", championship


#ecrire la fonction add_championship
add_championship(championship)


# for season in l1_file:
# 	new_season = dict()
# 	count = 1

# 	for day in l1_file[season]:
# 		new_season[str(count)] = list()

# 		for game in l1_file[season][day]:
# 			print "%s %s - %s %s" % (game[0][0], game[1][0], game[0][1], game[1][1])
# 			new_game = {
# 				"team_H": game[0][0],
# 				"team_A": game[0][1],
# 				"score": {
# 					"score_H": game[1][0],
# 					"score_A": game[1][1]
# 				}
# 			}
# 			game_id = mongo.add_game(new_game)
# 			new_season[str(count)].append(game_id)
# 		count += 1

# 	#ecrire la fonction add_season
# 	mongo.add_season("ligue_1", new_season, "%s/%s" % (int(season-1) int(season)))