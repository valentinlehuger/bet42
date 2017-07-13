from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import SoftmaxLayer
from sklearn import preprocessing
from collections import Counter
from datasetlib import buildDataset
from progressbar import Percentage, Bar, ETA, ProgressBar
import scipy
import numpy
import operator
import csv
import sys
import random

# def buildDataset():
#     with open(sys.argv[1], 'rb') as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=',')
#         dataXAll = list()
#         dataYAll = list()
#         cotationAll = list()
#         for i, rowdata in enumerate(spamreader):
#             row = list(rowdata)
#             HDA_cotation_col = range(len(row) - 3 - 1, len(row) - 1) # determine in which columns the cotations are
#             cotationHDA = list()
#             for j in HDA_cotation_col:
#                 cotationHDA.append(float(rowdata[j])) # retrieve cotation
#             for j in sorted(HDA_cotation_col, reverse=True):
#                 row.pop(j) # remove coations from the row before register the row into the training data
#             cotationAll.append(cotationHDA) # add cotations for the row in the cotationAll list
#             if i == 0:
#                 nfeatures = len(row) - 1
#             dataXAll.append([float(val) for val in row[0:nfeatures]])
#             if int(row[nfeatures]) == 1:
#                 dataYAll.append([1, 0, 0])
#             elif int(row[nfeatures]) == 0:
#                 dataYAll.append([0, 1, 0])
#             else:
#                 dataYAll.append([0, 0, 1])
#     return dataXAll, dataYAll, cotationAll

def linebet(state, net, datapX, datapY, cotationpHDA, scalizer, normalizer, with_bet):
    unit_bet = state["pct_bet"] * state["money"] if state["pct_bet"] * state["money"] > 0.5 else 0
    toPredict = [datapX[i] for i in xrange(0, len(datapX))]
    if scalizer is not None:
        toPredict = [scalizer.transform(toPredict[i]) for i in xrange(0, len(datapX))]
    if normalizer is not None:
        toPredict = [normalizer.transform(toPredict)[i] for i in xrange(0, len(datapX))]
    prediction = [net.activate(toPredict[i]) for i in xrange(0, len(datapX))]
    indexp = [(max(enumerate(prediction[i]), key=operator.itemgetter(1)))[0] for i in xrange(0, len(datapX))]
    indexe = [(max(enumerate(datapY[i]), key=operator.itemgetter(1)))[0] for i in xrange(0, len(datapX))]
    if (with_bet is True):
        state["money"] = state["money"] - unit_bet * len(datapX)
        unit_gain = [unit_bet * cotationpHDA[i][indexp[i]] if indexp[i] == indexe[i] else 0. for i in xrange(0, len(datapX))]
    else:
        unit_gain = [0]
    state["money"] += sum(unit_gain)
    state["win"] += sum([1 if indexp[i] == indexe[i] else 0 for i in xrange(0, len(datapX))])
    state["money_during_crossval_history"].append(state["money"])
    state["odds_during_crossval_history"].append(cotationpHDA)
    state["prediction_during_crossval_history"].append(prediction)
    state["expected_during_crossval_history"].append(indexe)
    state["predict_interpret_during_crossval_history"].append(indexp)
    return state

def crossvalidation(net, init_state, datapX, datapY, cotationpHDA, scalizer, normalizer, with_bet):
    crossvalidation_state = {"win" : 0,
                             "money" : init_state["moneyBase"],
                             "pct_bet" : init_state["pct_bet"],
                             "money_during_crossval_history" : list(),
                             "odds_during_crossval_history" : list(),
                             "prediction_during_crossval_history" : list(),
                             "predict_interpret_during_crossval_history" : list(),
                             "expected_during_crossval_history" : list()
    }
    for i in xrange(0, len(datapX), init_state["simult_bet"]):
        crossvalidation_state = linebet(crossvalidation_state, net, datapX[i:i + init_state["simult_bet"]], datapY[i:i + init_state["simult_bet"]], cotationpHDA[i:i + init_state["simult_bet"]], scalizer, normalizer, with_bet)
    return crossvalidation_state

def simulation(params, progressbar=True):
    ntry = params["ntry"]
    maxEpk = params["maxEpok"]
    normalize_data = params["normalize"]
    scale_data = params["scale"]
    crossvalidation_pct = params["cross_validation_percentage"]
    learningRate = params["algorithm"]["params"]["learning_rate"]
    moment = params["algorithm"]["params"]["momentum"]
    bet_simulation = params["bet_simulation"]

    # dataXAll, dataYAll, cotationAll = buildDataset()
    dataXAll, dataYAll, cotationAll = buildDataset(params["dataset"]["src"], params["dataset"]["features"], bet_simulation, mongolab=True) ################ !
    dataXAll = [[float(x) for x in row] for row in dataXAll]
    dataYAll = [[float(x) for x in row] for row in dataYAll]
    nfeatures = len(dataXAll[0])

    #################################
    # game_issue = [1, 0, -1]
    # for i in range(0, len(dataXAll)):
    #     print ",".join(str(x) for x in [dataXAll[i] + cotationAll[i] + [game_issue[max(enumerate(dataYAll[i]), key=operator.itemgetter(1))[0]]]])
    # exit (-1)
    #################################

    # stat variable init
    winrate_history_train = list()
    winrate_history = list()
    money_post_crossval_history = list()
    money_during_crossval_history = list()
    odds_during_crossval_history = list()
    prediction_during_crossval_history = list()
    predict_interpret_during_crossval_history = list()
    expected_during_crossval_history = list()
    init_state = {"moneyBase" : params["start_money"],
                  "pct_bet" : params["percentage_bet"],
                  "simult_bet" : params["simult_bet"]
    }
    # / stat variable init

    # Progress bar init
    if progressbar is True:
        widgets_pb = [Percentage(), ' ', Bar(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets_pb, maxval=ntry)
        pbar.start()
    # / Progress bar init

    for n in range(0, ntry):
        ds = SupervisedDataSet(nfeatures, 3)
        dataX = list(dataXAll)
        dataY = list(dataYAll)
        cotations = list(cotationAll)

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

        # crossvalidation randomization
        if params["cross_validation_randomize"] is True:
            combined_crossval_data = zip(datapX, datapY, cotationpHDA)
            random.shuffle(combined_crossval_data)
            datapX, datapY, cotationpHDA = zip(*combined_crossval_data)
        # / crossvalidation randomization

        # scalarization && normalization -->
        # http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html &&
        # http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Normalizer.html
        scalizer = None
        normalizer = None
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
        net = buildNetwork(ds.indim, (ds.indim + ds.outdim) / 2, (ds.indim + ds.outdim) / 2, ds.outdim, bias=True, outclass=SoftmaxLayer) # building the n
        trainer = BackpropTrainer(net, ds, learningrate=learningRate, momentum=moment, verbose=False) # building the trainer
        # / nn && trainer construction

        # training
        trainer.trainUntilConvergence(maxEpochs=maxEpk) # Train, until convergence
        # for epoch in range(0,1000):
        #         trainer.train()
        # / training

        # crossvalidation on training data
        post_crossval_state = crossvalidation(net, init_state, dataX, dataY, cotations, scalizer, normalizer, False)
        # / crossvalidation on training data

        # post crossvalidation training data data register
        winrate = post_crossval_state["win"] / float(len(dataX))
        winrate_history_train.append(winrate)
        # / post crossvalidation training data data register

        # crossvalidation
        post_crossval_state = crossvalidation(net, init_state, datapX, datapY, cotationpHDA, scalizer, normalizer, bet_simulation)
        # / crossvalidation

        # post unit crossvalidation data register
        winrate = post_crossval_state["win"] / float(len(datapX))
        winrate_history.append(winrate)
        money_post_crossval_history.append(post_crossval_state["money"])
        money_during_crossval_history.append(post_crossval_state["money_during_crossval_history"])
        odds_during_crossval_history.append(post_crossval_state["odds_during_crossval_history"])
        prediction_during_crossval_history.append(post_crossval_state["prediction_during_crossval_history"])
        predict_interpret_during_crossval_history.append(post_crossval_state["predict_interpret_during_crossval_history"])
        expected_during_crossval_history.append(post_crossval_state["expected_during_crossval_history"])
        # / post unit crossvalidation data register

        if progressbar is True:
            pbar.update(n + 1)
    # scipy.describe instantiation
    winrate_history_describe_train = scipy.stats.describe(winrate_history_train)
    winrate_history_describe = scipy.stats.describe(winrate_history)
    money_post_crossval_history_describe = scipy.stats.describe(money_post_crossval_history)
    # / scipy.describe instantiation
    if progressbar is True:
        pbar.finish()
    results = {"win_percentage_training" : {"median" : numpy.median(numpy.array(winrate_history_train)),
                                            "standard_deviation" : numpy.std(numpy.array(winrate_history_train)),
                                            "variance" : numpy.var(numpy.array(winrate_history_train)),
                                            "mode" : scipy.stats.mstats.mode([round(w, 2) for w in winrate_history_train]),
                                            "describe" : {"nobs" : winrate_history_describe_train[0],
                                                          "min" : winrate_history_describe_train[1][0],
                                                          "max" : winrate_history_describe_train[1][1],
                                                          "mean" : winrate_history_describe_train[2],
                                                          "variance" : winrate_history_describe_train[3],
                                                          "skewness" : winrate_history_describe_train[4],
                                                          "kurtosis" : winrate_history_describe_train[5]
                                                      },
                                   "normal_test" : scipy.stats.normaltest(winrate_history_train),
                                   "histogram" : scipy.stats.histogram(winrate_history_train),
                                   "lst" : winrate_history_train
                                   },
               "win_percentage" : {"median" : numpy.median(numpy.array(winrate_history)),
                                   "standard_deviation" : numpy.std(numpy.array(winrate_history)),
                                   "variance" : numpy.var(numpy.array(winrate_history)),
                                   "mode" : scipy.stats.mstats.mode([round(w, 2) for w in winrate_history]),
                                   "describe" : {"nobs" : winrate_history_describe[0],
                                                 "min" : winrate_history_describe[1][0],
                                                 "max" : winrate_history_describe[1][1],
                                                 "mean" : winrate_history_describe[2],
                                                 "variance" : winrate_history_describe[3],
                                                 "skewness" : winrate_history_describe[4],
                                                 "kurtosis" : winrate_history_describe[5]
                                             },
                                   "normal_test" : scipy.stats.normaltest(winrate_history),
                                   "histogram" : scipy.stats.histogram(winrate_history),
                                   "lst" : winrate_history
                                   },
               "money_during_cross_validation" : {"min" : min([item for sublist in money_during_crossval_history for item in sublist]),
                                                  "max" : max([item for sublist in money_during_crossval_history for item in sublist]),
                                                  "lst" : money_during_crossval_history
                                                  },
               "odds_during_crossval_history" : {
                                                  "lst" : odds_during_crossval_history
                                                  },
               "prediction_during_crossval_history" : {
                                                  "lst" : prediction_during_crossval_history
                                                  },
               "predict_interpret_during_crossval_history" : {
                                                  "lst" : predict_interpret_during_crossval_history
               },
               "expected_during_crossval_history" : {
                   "lst" : expected_during_crossval_history
               },
               "money_post_cross_validation" : {"median" : numpy.median(numpy.array(money_post_crossval_history)),
                                                "standard_deviation" : numpy.std(numpy.array(money_post_crossval_history)),
                                                "variance" : numpy.var(numpy.array(money_post_crossval_history)),
                                                "mode" : scipy.stats.mstats.mode([round(m, 1) for m in money_post_crossval_history]),
                                                "describe" : {"nobs" : money_post_crossval_history_describe[0],
                                                              "min" : money_post_crossval_history_describe[1][0],
                                                              "max" : money_post_crossval_history_describe[1][1],
                                                              "mean" : money_post_crossval_history_describe[2],
                                                              "variance" : money_post_crossval_history_describe[3],
                                                              "skewness" : money_post_crossval_history_describe[4],
                                                              "kurtosis" : money_post_crossval_history_describe[5]
                                                          },
                                                "normal_test" : scipy.stats.normaltest(money_post_crossval_history),
                                                "histogram" : scipy.stats.histogram(money_post_crossval_history),
                                                "lst" : money_post_crossval_history
                                                }
               }
    return results

if __name__ == "__main__":
# 55908dfe9734042e6bbd4359 Premier League ID
# 55908dfe9734042e6bbd435f Bundesliga
    params_simu = {"ntry" : 100,
                   "maxEpok" : 200,
                   "normalize" : True,
                   "scale" : False,
                   "cross_validation_percentage" : 0.3,
                   "cross_validation_randomize" : True,
                   "bet_simulation" : True,
                   "dataset" : {"src" : [
                            ["55908dfe9734042e6bbd4359", "2011_08_01", "2015_07_01"],
                            ["55908bc3973404160f0566a6", "2011_08_01", "2015_07_01"],
                        ],
                                "features" : ["last_seven_results", "ranking", "day", "last_seven_goals", "last_seven_home_or_away", "last_seven_shots", "last_seven_goals_per_shots", "last_seven_rankings"]
                                },
                   "algorithm" : {"name" : "nn",
                                  "params" : {"learning_rate" : 0.5, "momentum" : 0.}},
                   "start_money" : 100.,
                   "percentage_bet" : 0.05,
                   "simult_bet" : 10
                   }
    # print params_simu
    # print "\n"
    results = simulation(params_simu)
    print params_simu, "\n"

    print "For each n simulation, where k is the number of simultaneous bet during crossvalidation, there is:"
    print "Simulation n"
    print "success rate (good prediction / total prediction), money at the end"
    print "prediction index 0, ..., prediction index k, expected prediction 0, ..., expected prediction k, odd H 0, odd D 0, odd A 0, ..., odd H k, odd D k, odd A k, prediction H 0, prediction D 0, prediction A 0, ..., prediction H k, prediction D k, prediction A k, money\n"

    for idx_simulation, win_pct in enumerate(results["win_percentage"]["lst"]):
        print results["win_percentage"]["lst"][idx_simulation], results["money_post_cross_validation"]["lst"][idx_simulation]
        for idx_betline, prediction_interpret in enumerate(results["predict_interpret_during_crossval_history"]["lst"][idx_simulation]):
            betline_history = results["predict_interpret_during_crossval_history"]["lst"][idx_simulation][idx_betline] +\
                              results["expected_during_crossval_history"]["lst"][idx_simulation][idx_betline] +\
                              [val for sublist in results["odds_during_crossval_history"]["lst"][idx_simulation][idx_betline] for val in sublist] +\
                              [val for sublist in results["prediction_during_crossval_history"]["lst"][idx_simulation][idx_betline] for val in sublist] +\
                              [results["money_during_cross_validation"]["lst"][idx_simulation][idx_betline]]
            print ",".join([str(x) for x in betline_history])
        print ""

    print "GLOBAL RESULTS:"
    print "\tWin percentage"
    print "\t\tmin:", results["win_percentage"]["describe"]["min"]
    print "\t\tmax:", results["win_percentage"]["describe"]["max"]
    print "\t\tmean:", results["win_percentage"]["describe"]["mean"]
    print "\t\tmedian:", results["win_percentage"]["median"]
    print "\t\tstandard deviation:", results["win_percentage"]["standard_deviation"]
    print "\t\tmode:", results["win_percentage"]["mode"]
    print "\t\thistogram:", results["win_percentage"]["histogram"]
    print "\tMoney post cross validation"
    print "\t\tmin:", results["money_post_cross_validation"]["describe"]["min"]
    print "\t\tmax:", results["money_post_cross_validation"]["describe"]["max"]
    print "\t\tmean:", results["money_post_cross_validation"]["describe"]["mean"]
    print "\t\tmedian:", results["money_post_cross_validation"]["median"]
    print "\t\tstandard deviation:", results["money_post_cross_validation"]["standard_deviation"]
    print "\t\tmode:", results["money_post_cross_validation"]["mode"]
    print "\t\thistogram:", results["money_post_cross_validation"]["histogram"]
