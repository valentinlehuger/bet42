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
maxEpk = 10
normalize_data = 1
scale_data = 0
crossvalidation_pct = 0.3
unit_bet = 1

if len(sys.argv) != 2:
    print "usage: py nn.py training.csv"
    exit (-1)

with open(sys.argv[1], 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    dataXAll = list()
    dataYAll = list()
    cotationAll = list()
    for i, rowdata in enumerate(spamreader):
        row = list(rowdata)
        HDA_cotation_col = range(len(row) - 3 - 1, len(row) - 1) # determine in which columns the cotations are 
        cotationHDA = list()
        for j in HDA_cotation_col:
            cotationHDA.append(float(rowdata[j])) # retrieve cotation
        for j in sorted(HDA_cotation_col, reverse=True):
            row.pop(j) # remove coations from the row before register the row into the training data
        cotationAll.append(cotationHDA) # add cotations for the row in the cotationAll list
        if i == 0:
            nfeatures = len(row) - 1
        dataXAll.append([float(val) for val in row[0:nfeatures]])
        if int(row[nfeatures]) == 1:
            dataYAll.append([1, 0, 0])
        elif int(row[nfeatures]) == 0:
            dataYAll.append([0, 1, 0])
        else:
            dataYAll.append([0, 0, 1])

# stat variable init
winrateFinal = 0.
winrateMin = winrateFinal
winrateMax = winrateFinal
moneyFinal = 0.
moneyMinSeason = moneyFinal
moneyMaxSeason = moneyFinal
cotationMeanFinal = 0.
cotationMeanMin = 0.
cotationMeanMax = 0.
moneyBase = 100
moneyMin = moneyBase
moneyMax = moneyBase
# / stat variable init

print "n, -->  n winrate | n money balance --> mean winrate | mean money balance"
for n in range(0, ntry):
    ds = SupervisedDataSet(nfeatures, 3)
    dataX = list(dataXAll)
    dataY = list(dataYAll)
    cotations = list(cotationAll)

    # # crossvalidation data construction RANDOM PICK
    # datapX = list()
    # datapY = list()
    # cotationpHDA = list()
    # for i in range(0, int(crossvalidation_pct * len(dataX))):
    #     popi = random.randint(0, len(dataX) - 1)
    #     datapX.append(dataX[popi])
    #     datapY.append(dataY[popi])
    #     cotationpHDA.append(cotations[popi])
    #     dataX.pop(popi)
    #     dataY.pop(popi)
    #     cotations.pop(popi)
    # # / crossvalidation data construction

    # crossvalidation data construction PICK LAST
    datapX = list()
    datapY = list()
    cotationpHDA = list()
    extracti = int(len(dataX) - (crossvalidation_pct * len(dataX)))
    datapX = dataX[extracti:len(dataX)]
    datapY = dataY[extracti:len(dataY)]
    cotationpHDA = cotations[extracti:len(cotations)]
    dataX = dataX[0:extracti]
    dataY = dataY[0:extracti]
    cotations = cotations[0:extracti]
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
    trainer = BackpropTrainer(net, ds, learningrate=0.3, momentum=0, verbose=False) # building the trainer
    # / nn && trainer construction

    # training
    trainer.trainUntilConvergence(maxEpochs=maxEpk) # Train, until convergence
    # for epoch in range(0,1000):
    #         trainer.train()
    # / training

    # cross validation
    win = 0
    money = moneyBase
    cotationMean = 0.
    for i in range(0, len(datapX)):
        unit_bet = 6. / 100. * money if 6. / 100. * money > 0.5 else 0
        toPredict = datapX[i]
        if scale_data == 1:
            toPredict = scalizer.transform(toPredict)
        if normalize_data == 1:
            toPredict = normalizer.transform(toPredict)[0]
        prediction = net.activate(toPredict)
        indexp, valuep = max(enumerate(prediction), key=operator.itemgetter(1))
        indexe, valuee = max(enumerate(datapY[i]), key=operator.itemgetter(1))
        money = money - unit_bet # bet unit_bet on the prediction (money is lost)
        cotationMean += cotationpHDA[i][indexp]
        if indexp == indexe:
            win = win + 1
            money = money + (unit_bet * cotationpHDA[i][indexp]) # on good prediction, money increased by unit_bet * predicted issue cotation
            print >> sys.stderr, money
        # in crossvalidation money min/max retrieve
        moneyMin = money if money < moneyMin else moneyMin
        moneyMax = money if money > moneyMax else moneyMax
        # / in crossvalidation money min/max retrieve
    # / cross validation
    cotationMean = cotationMean / float(len(datapX))
    cotationMeanFinal += cotationMean
    winrate = win / float(len(datapX))
    winrateFinal += winrate
    moneyFinal += money # accumulator for post simulation calculation mean money
    # post crossvalidation money min/max retrieve
    if n == 0:
        winrateMin = winrate
        winrateMax = winrate
        moneyMinSeason = money
        moneyMaxSeason = money
        cotationMeanMin = cotationMean
        cotationMeanMax = cotationMean
    else:
        winrateMin = winrate if winrate < winrateMin else winrateMin
        winrateMax = winrate if winrate > winrateMax else winrateMax
        moneyMinSeason = money if money < moneyMinSeason else moneyMinSeason
        moneyMaxSeason = money if money > moneyMaxSeason else moneyMaxSeason
        cotationMeanMin = cotationMean if cotationMean < cotationMeanMin else cotationMeanMin
        cotationMeanMax = cotationMean if cotationMean > cotationMeanMax else cotationMeanMax
    # / post crossvalidation money min/max retrieve
    print >> sys.stderr, n + 1, "/", ntry, " --> ", winrate * 100 , " | ", money, " --> ", float(winrateFinal) / float(n + 1) * 100, " | ", float(moneyFinal) / float(n + 1)
print "Final win rate min | mean | max: ", winrateMin * 100, " | ", float(winrateFinal) / float(ntry) * 100, " | ", winrateMax * 100
print "Final (during crossvalidation) min money | max money:", moneyMin, " | ", moneyMax
print "Final (post crossvalidation) money min | mean | max:", moneyMinSeason, " | ", float(moneyFinal) / float(ntry), " | ", moneyMaxSeason
print "Final cotation min | mean | max:", cotationMeanMin, " | ", cotationMeanFinal / float(ntry), " | ", cotationMeanMax

