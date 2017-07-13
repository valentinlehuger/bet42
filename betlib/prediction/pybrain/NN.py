from pybrain.datasets import SupervisedDataSet
from betlib.simulation.pybrain.datasetlib import buildDataset
from betlib.simulation.pybrain.datasetlib import load_game_id_features
from betlib.mongo import get_db, insert, find_one
from sklearn import preprocessing
from pybrain.tools.shortcuts import buildNetwork
from progressbar import Percentage, Bar, ETA, ProgressBar
from pybrain.structure import SoftmaxLayer
from pybrain.supervised.trainers import BackpropTrainer
from bson.binary import Binary
import os
import sys
import cPickle
import pickle

class NN(object):

    def __init__(self, params=None):
        self.params = params
        self.scalizer = None
        self.normalizer = None
        self.client_db = None
        if params is not None:
            self.nn = self._build_nn()

    def load_from_file(self, filename):
        file_object = open(filename, 'r')
        self.params, self.nn, self.scalizer, self.normalizer = cPickle.load(file_object)
        file_object.close()

    def save_to_file(self, filename):
        to_save = (self.params, self.nn, self.scalizer, self.normalizer)
        file_object = open(filename, 'w')
        cPickle.dump(to_save, file_object)
        file_object.close()

    def save_to_db(self, name):
        if self.client_db is None:
            self.client_db = get_db("prono", mongolab=True)
        to_save = {
            "name": name,
            "params": self.params,
            "nn": pickle.dumps(self.nn),
            "scalizer": pickle.dumps(self.scalizer),
            "normalizer": pickle.dumps(self.normalizer)
        }
        return insert(to_save, "prono", "learning_objects", connection=self.client_db)

    def load_from_db(self, name):
        if self.client_db is None:
            self.client_db = get_db("prono", mongolab=True)
        db_obj = find_one({"name": name}, "prono", "learning_objects", connection=self.client_db)
        self.name = db_obj["name"]
        self.params = db_obj["params"]
        self.nn = pickle.loads(db_obj["nn"])
        self.scalizer = pickle.loads(db_obj["scalizer"])
        self.normalizer = pickle.loads(db_obj["normalizer"])


    def predict(self, games_id_list):
        prediction = list()
        for game_id in games_id_list:
            game_features = load_game_id_features(game_id, self.params["dataset"]["features"], mongolab=True)
            to_predict = [float(x) for x in game_features]
            if self.params["scale"] == True:
                to_predict = self.scalizer.transform(to_predict)
            if self.params["normalize"] == True:
                to_predict = self.normalizer.transform(to_predict)[0]
            prediction.append(self.nn.activate(to_predict))
            print game_id, self.nn.activate(to_predict)
        return prediction

    def _build_nn(self):
        learning_rate = self.params["algorithm"]["params"]["learning_rate"]
        moment = self.params["algorithm"]["params"]["momentum"]
        epok = self.params["epok"]
        dataX, dataY, cotation = buildDataset(self.params["dataset"]["src"], self.params["dataset"]["features"], False, mongolab=True)
        dataX = [[float(x) for x in row] for row in dataX]
        dataY = [[float(x) for x in row] for row in dataY]
        nfeatures = len(dataX[0])
        ds = SupervisedDataSet(nfeatures, 3)
        if self.params["scale"] == True:
            self.scalizer = preprocessing.StandardScaler().fit(dataX)
            dataX = self.scalizer.transform(dataX)
        if self.params["normalize"] == True:
            self.normalizer = preprocessing.Normalizer().fit(dataX)
            dataX = self.normalizer.transform(dataX)
        for i in range(0, len(dataX)):
            ds.addSample(dataX[i], dataY[i])
        net = buildNetwork(ds.indim, (ds.indim + ds.outdim) / 2, ds.outdim, bias=True, outclass=SoftmaxLayer)
        trainer = BackpropTrainer(net, ds, learningrate=learning_rate, momentum=moment, verbose=False)
        print >> sys.stderr, "Training start..."
        # Progress bar init
        widgets_pb = [Percentage(), ' ', Bar(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets_pb, maxval=epok)
        pbar.start()
    # / Progress bar init
        for epoch in xrange(0,epok):
            trainer.train()
            pbar.update(epoch + 1)
        pbar.finish()
        return net





# if __name__ == "__main__":
#     params_simu = {"epok" : 10,
#                    "normalize" : True,
#                    "scale" : False,
#                    "dataset" : {"src" : [["55908dfe9734042e6bbd4359", "2011_08_01", "2014_07_01"], ["55908dfe9734042e6bbd4360", "2011_08_01", "2014_07_01"]],
#                                 "features" : ["last_seven_results", "ranking", "day", "last_seven_goals", "last_seven_home_or_away", "last_seven_rankings"]
#                                 },
#                    "algorithm" : {"name" : "nn",
#                                   "params" : {"learning_rate" : 0.5, "momentum" : 0.}},
#                    }
#     # antoine_le_robot = NN(params_simu)
#     # antoine_le_robot.save_to_file("antoine.nn")
#     predicator = NN()
#     predicator.load_from_file("antoine.nn")
#     # predicator.save_to_db("antoine")
#     # predicator_return = NN()
#     predicator.load_from_db("antoine")
#     # assert jack_le_copieur.params == antoine_le_robot.params
#     print predicator.predict(["55abe63c1461574dfd8ecc7b", "55abe63c1461574dfd8ecc7c", "55abe63c1461574dfd8ecc79", "55abe63c1461574dfd8ecc7a", "55abe63c1461574dfd8ecc7d", "55abe63c1461574dfd8ecc7e", "55abe63c1461574dfd8ecc7f", "55abe63c1461574dfd8ecc80", "55abe63c1461574dfd8ecc81"])
#     # os.remove("antoine.nn")
