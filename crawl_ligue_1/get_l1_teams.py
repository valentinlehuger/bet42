import json


with open("resultat_ligue_1.json", "r") as ligue1_file:
	l1_file = json.load(ligue1_file)


teams = set()
for season in l1_file:
	for day in l1_file[season]:
		for game in l1_file[season][day]:
			for team in game[0]:
				teams.add(team)


for team in teams:
	print team

print
print len(teams)