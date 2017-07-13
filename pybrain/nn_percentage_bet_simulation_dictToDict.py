from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import SoftmaxLayer
from sklearn import preprocessing
import numpy
import operator
import csv
import sys
import random

def buildDataset(srcs, features):
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
    return dataXAll, dataYAll, cotationAll

def simulation(params):
    ntry = params["ntry"]
    maxEpk = params["maxEpok"]
    normalize_data = params["normalize"]
    scale_data = params["scale"]
    crossvalidation_pct = params["cross_validation_percentage"]
    learningRate = params["algorithm"]["params"]["learning_rate"]
    moment = params["algorithm"]["params"]["momentum"]

    dataXAll, dataYAll, cotationAll = buildDataset(params["dataset"]["src"], params["dataset"]["features"])
    nfeatures = len(dataXAll[0])
    # stat variable init
    winrateLst = list()
    moneyLst = list()
    cotationMeanLst = list()
    moneyBase = params["start_money"]
    moneyMin = moneyBase
    moneyMax = moneyBase
    pct_bet = params["percentage_bet"]
    # / stat variable init
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
        if scale_data == True:
            scalizer = preprocessing.StandardScaler().fit(dataX)
            dataX = scalizer.transform(dataX)
        if normalize_data == True:
            normalizer = preprocessing.Normalizer().fit(dataX)
            dataX = normalizer.transform(dataX)
        # / scalarization && normalization

        # training dataset construction
        for i in range(0, len(dataX)):
            ds.addSample(dataX[i], dataY[i])
        # / training dataset construction

        # nn && trainer construction
        net = buildNetwork(ds.indim, (ds.indim + ds.outdim) / 2, ds.outdim, bias=True, outclass=SoftmaxLayer) # building the n
        trainer = BackpropTrainer(net, ds, learningrate=learningRate, momentum=moment, verbose=False) # building the trainer
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
            unit_bet = pct_bet * money if pct_bet * money > 0.5 else 0
            toPredict = datapX[i]
            if scale_data == True:
                toPredict = scalizer.transform(toPredict)
            if normalize_data == True:
                toPredict = normalizer.transform(toPredict)[0]
            prediction = net.activate(toPredict)
            indexp, valuep = max(enumerate(prediction), key=operator.itemgetter(1))
            indexe, valuee = max(enumerate(datapY[i]), key=operator.itemgetter(1))
            money = money - unit_bet # bet unit_bet on the prediction (money is lost)
            cotationMean += cotationpHDA[i][indexp]
            if indexp == indexe:
                win = win + 1
                money = money + (unit_bet * cotationpHDA[i][indexp]) # on good prediction, money increased by unit_bet * predicted issue cotation
            # in crossvalidation money min/max retrieve
            moneyMin = money if money < moneyMin else moneyMin
            moneyMax = money if money > moneyMax else moneyMax
            # / in crossvalidation money min/max retrieve
            # / cross validation
        cotationMean = cotationMean / float(len(datapX))
        cotationMeanLst.append(cotationMean)
        winrate = win / float(len(datapX))
        winrateLst.append(winrate)
        moneyLst.append(money)
    winrateFinal = sum(winrateLst) / float(ntry)
    winrateMin = min(winrateLst)
    winrateMax = max(winrateLst)
    winrateMedian = numpy.median(numpy.array(winrateLst))
    winrateStdDev = numpy.std(numpy.array(winrateLst))
    moneyFinal = sum(moneyLst) / float(ntry)
    moneyMinSeason = min(moneyLst)
    moneyMaxSeason = max(moneyLst)
    moneyMedian = numpy.median(numpy.array(moneyLst))
    moneyStdDev = numpy.std(numpy.array(moneyLst))
    cotationMeanFinal = sum(cotationMeanLst) / float(ntry)
    cotationMeanMin = min(cotationMeanLst)
    cotationMeanMax = max(cotationMeanLst)
    cotationMeanMedian = numpy.median(numpy.array(cotationMeanLst))
    cotationMeanStdDev = numpy.std(numpy.array(cotationMeanLst))
    results = {"win_percentage" : {"min" : winrateMin,
                                   "max" : winrateMax,
                                   "mean" : winrateFinal,
                                   "median" : winrateMedian,
                                   "standard_deviation" : winrateStdDev,
                                   "lst" : winrateLst
                                   },
               "money_during_cross_validation" : {"min" : moneyMin,
                                                  "max" : moneyMax
                                                  },
               "money_post_cross_validation" : {"min" : moneyMinSeason,
                                                "max" : moneyMaxSeason,
                                                "mean" : moneyFinal,
                                                "median" : moneyMedian,
                                                "standard_deviation" : moneyStdDev,
                                                "lst" : moneyLst
                                                },
               "mean_cotation" : {"min" : cotationMeanMin,
                                  "max" : cotationMeanMax,
                                  "mean" : cotationMeanFinal,
                                  "median" : cotationMeanMedian,
                                  "standard_deviation" : cotationMeanStdDev,
                                  "lst" : cotationMeanLst
                                  }
               }
    print results
    return results

if len(sys.argv) != 2:
    print "usage: py nn.py training.csv"
    exit (-1)

params_simu = {"ntry" : 10,
               "maxEpok" : 10,
               "normalize" : True,
               "scale" : True,
               "cross_validation_percentage" : 0.3,
               "dataset" : {"src" : [["unIdDeCompet", "2014_08_10", "2015_03_01"], ["unIdDeCompet", "2014_08_10", "2015_03_01"]],
                            "features" : ["last7results", "ranking"]
                            },
               "algorithm" : {"name" : "nn",
                              "params" : {"learning_rate" : 0.1, "momentum" : 0.}},
               "start_money" : 100.,
               "percentage_bet" : 0.06
               }

simulation(params_simu)
