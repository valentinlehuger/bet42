from operator import itemgetter
import csv
import os

def get_rank(points, team):
    rank = 1
    team_points = points[team][0]
    for t in points:
        if t != team and points[t][0] > team_points:
            rank += 1
    return rank


datas = list()

with open(os.sys.argv[1], 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    datas = sorted([l for l in csvreader], key=itemgetter(0))

classement = dict()

final = list()
for game in datas:
    if game[1] not in classement:
        classement[game[1]] = [0, 0]
    if game[2] not in classement:
        classement[game[2]] = [0, 0]

    classement[game[1]][1] += 1
    classement[game[2]][1] += 1
    
    s_h, s_a = [int(x) for x in game[3].split(' - ')]
    if s_h > s_a:
        classement[game[1]][0] += 3
    elif s_h < s_a:
        classement[game[2]][0] += 3
    else:
        classement[game[1]][0] += 1
        classement[game[2]][0] += 1
    final.append(game + [str(get_rank(classement, game[1])), str(get_rank(classement, game[2])), str(classement[game[1]][1])])



for l in final:
    print ",".join(l)
