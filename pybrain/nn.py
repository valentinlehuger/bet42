from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import SoftmaxLayer
from sklearn import preprocessing
import operator
import csv
import sys
import random


ntry = 10
maxEpk = 100
normalize_data = 1
scale_data = 0
crossvalidation_pct = 0.3

if len(sys.argv) != 2:
    print "usage: py nn.py training.csv"
    exit (-1)

with open(sys.argv[1], 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    dataXAll = list()
    dataYAll = list()
    for i, row in enumerate(spamreader):
        if i == 0:
            nfeatures = len(row) - 1
        dataXAll.append([float(val) for val in row[0:nfeatures]])
        if int(row[nfeatures]) == 1:
            dataYAll.append([1, 0, 0])
        elif int(row[nfeatures]) == 0:
            dataYAll.append([0, 1, 0])
        else:
            dataYAll.append([0, 0, 1])

winrateFinal = 0
winrateMin = winrateFinal
winrateMax = winrateFinal
for n in range(0, ntry):
    ds = SupervisedDataSet(nfeatures, 3)
    dataX = list(dataXAll)
    dataY = list(dataYAll)

    # # crossvalidation data construction RANDOM PICK
    # datapX = list()
    # datapY = list()
    # for i in range(0, int(crossvalidation_pct * len(dataX))):
    #     popi = random.randint(0, len(dataX) - 1)
    #     datapX.append(dataX[popi])
    #     datapY.append(dataY[popi])
    #     dataX.pop(popi)
    #     dataY.pop(popi)
    # # / crossvalidation data construction

    # crossvalidation data construction PICK LAST
    datapX = list()
    datapY = list()
    extracti = int(len(dataX) - (crossvalidation_pct * len(dataX)))
    datapX = dataX[extracti:len(dataX)]
    datapY = dataY[extracti:len(dataY)]
    dataX = dataX[0:extracti]
    dataY = dataY[0:extracti]
    # / crossvalidation data construction

    # scalarization && normalization -->
    # http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html &&
    # http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Normalizer.html
    if scale_data == 1:
        scalizer = preprocessing.StandardScaler().fit(dataX)
        dataX = scalizer.transform(dataX)
    if normalize_data == 1:
        normalizer = preprocessing.Normalizer().fit(dataX)
        dataX = normalizer.transform(dataX)
    # / scalarization && normalization

    # training dataset construction
    for i in range(0, len(dataX)):
        ds.addSample(dataX[i], dataY[i])
    # / training dataset construction

    # nn && trainer construction
    net = buildNetwork(ds.indim, (ds.indim + ds.outdim) / 2, ds.outdim, bias=True, outclass=SoftmaxLayer) # building the n
    trainer = BackpropTrainer(net, ds, learningrate=0.15, momentum=0, verbose=False) # building the trainer
    # / nn && trainer construction

    # training
    trainer.trainUntilConvergence(maxEpochs=maxEpk) # Train, until convergence
    # for epoch in range(0,1000):
    #         trainer.train()
    # / training

    # cross validation
    win = 0
    for i in range(0, len(datapX)):
        toPredict = datapX[i]
        if scale_data == 1:
            toPredict = scalizer.transform(toPredict)
        if normalize_data == 1:
            toPredict = normalizer.transform(toPredict)[0]
        prediction = net.activate(toPredict)
        indexp, valuep = max(enumerate(prediction), key=operator.itemgetter(1))
        indexe, valuee = max(enumerate(datapY[i]), key=operator.itemgetter(1))
        if indexp == indexe:
            win = win + 1
    # / cross validation
    winrate = float(win) / float(len(datapX))
    winrateFinal += winrate
    if n == 0:
        winrateMin = winrate
        winrateMax = winrate
    else:
        winrateMin = winrate if winrate < winrateMin else winrateMin
        winrateMax = winrate if winrate > winrateMax else winrateMax
    print >> sys.stderr, n + 1, "/", ntry, " --> ", winrate * 100 , " --> ", float(winrateFinal) / float(n + 1) * 100
print "Final win rate min | mean | max: ", winrateMin * 100, " | ", float(winrateFinal) / float(ntry) * 100, " | ", winrateMax * 100
