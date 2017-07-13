from operator import itemgetter
import csv
import os

def score_to_label(lst):
    labels = list()
    for e in lst:
        if "-" not in e:
            labels.append(int(e))
        else:
            a,b = [int(y) for y in e.split(" - ")]
            if a < b:
                labels.append(-1)
            elif a == b:
                labels.append(0)
            else:
                labels.append(1)
    return labels


datas = list()

with open(os.sys.argv[1], 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    datas = sorted([l for l in csvreader], key=itemgetter(0))


ret = list()
for game in datas:
    team_H = game[1]
    team_A = game[2]
    last_result_H = list()
    last_result_A = list()
    for last_game in datas:
        if last_game[0] < game[0]:
            if team_H == last_game[1] or team_H == last_game[2]:
                last_result_H.append(last_game[3])
            if team_A == last_game[1] or team_A == last_game[2]:
                last_result_A.append(last_game[3][::-1])
    if len(last_result_H) >= 7 and len(last_result_A) >= 7:
        ret.append(last_result_H[-7:] + [game[4]] + last_result_A[-7:] + [game[5], game[6], game[3]])

for g in ret:
    if isinstance(g, list):
        print ",".join([str(x) for x in score_to_label(g)])
