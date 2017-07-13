import csv
import sys

col_to_extract = [49, 51, 53]
nline_to_extract = 118
reverse_extract = True

if len(sys.argv) != 3:
    print "usage: py script-append-football_data_co_uk.py origin.csv originextract.csv"
    exit (-1)

extracted_data = list()
with open(sys.argv[2], 'rb') as csvfile:
    if reverse_extract is True:
        reader = reversed(list(csv.reader(csvfile, delimiter=',')))
    else:
        reader = list(csv.reader(csvfile, delimiter=','))
    for i, row in enumerate(reader):
        if reverse_extract is False and i == 0:
            continue
        if i == nline_to_extract - (reverse_extract == False):
            break
        extracted_data.append([row[j] for j in col_to_extract])
if reverse_extract is True:
    extracted_data.reverse()
origin_data = list()
with open(sys.argv[1], 'rb') as csvfile:
    origin_data = list(csv.reader(csvfile, delimiter=','))
    if len(origin_data) != len(extracted_data):
        raise Exception, "len origin differ from len extracted data"

destination_data = list()
for idx, ori in enumerate(origin_data):
    destination_data = destination_data + [ori[0:len(ori) - 1] + extracted_data[idx] + ori[len(ori) - 1: len(ori)]]

for row in destination_data:
    print ",".join(map(str, row))
