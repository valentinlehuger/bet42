from nn import simulation
from multiprocessing import Pool
import pickle
import sys
import copy


def _construct_list_parameters(params_simu_list):
    params_ref = {"ntry" : None,
                   "maxEpok" : None,
                   "normalize" : None,
                   "scale" : None,
                   "cross_validation_percentage" : None,
                   "cross_validation_randomize" : None,
                   "bet_simulation" : params_simu_list["bet_simulation"],
                   "dataset" : {"src" : None,
                                "features" : None
                                },
                   "algorithm" : {"name" : params_simu_list["algorithm"]["name"],
                                  "params" : {"learning_rate" : None, "momentum" : None}},
                   "start_money" : None,
                   "percentage_bet" : None,
                   "simult_bet" : None
                   }
    params = list()
    for data_src in params_simu_list["dataset"]["src"]:
        for ntry in params_simu_list["ntry"]:
            for maxEpok in params_simu_list["maxEpok"]:
                for normalize in params_simu_list["normalize"]:
                    for scale in params_simu_list["scale"]:
                        for cvp in params_simu_list["cross_validation_percentage"]:
                            for cvr in params_simu_list["cross_validation_randomize"]:
                                for data_features in params_simu_list["dataset"]["features"]:
                                    for learning_rate in params_simu_list["algorithm"]["params"]["learning_rate"]:
                                        for momentum in params_simu_list["algorithm"]["params"]["momentum"]:
                                            for start_money in params_simu_list["start_money"]:
                                                for percentage_bet in params_simu_list["percentage_bet"]:
                                                    for simult_bet in params_simu_list["simult_bet"]:
                                                        new_param = copy.deepcopy(params_ref)
                                                        new_param["ntry"] = ntry
                                                        new_param["maxEpok"] = maxEpok
                                                        new_param["normalize"] = normalize
                                                        new_param["scale"] = scale
                                                        new_param["cross_validation_percentage"] = cvp
                                                        new_param["cross_validation_randomize"] = cvr
                                                        new_param["dataset"]["src"] = data_src
                                                        new_param["dataset"]["features"] = data_features
                                                        new_param["algorithm"]["params"]["learning_rate"] = learning_rate
                                                        new_param["algorithm"]["params"]["momentum"] = momentum
                                                        new_param["start_money"] = start_money
                                                        new_param["percentage_bet"] = percentage_bet
                                                        new_param["simult_bet"] = simult_bet
                                                        params.append(new_param)
    return params


def _simulation(param):
    result = {"parameter" : param}
    result["result"] = simulation(param, True)
    return result



def bulk_simulation(params_simu_list, nprocess=4):
    params_simulations = _construct_list_parameters(params_simu_list)
    print >> sys.stderr, "Number of simulation:", len(params_simulations)
    process = Pool(nprocess)
    return process.map(_simulation, params_simulations)




if __name__ == "__main__":
    param = {"ntry" : [10],
                   "maxEpok" : [10, 11],
                   "normalize" : [True],
                   "scale" : [False],
                   "cross_validation_percentage" : [0.1],
                   "cross_validation_randomize" : [False],
                   "bet_simulation" : True,
                   "dataset" : {"src" : [[
                            ["55908dfe9734042e6bbd4359", "2010_08_01", "2012_07_01"],
                        ], [
                            ["55908dfe9734042e6bbd4359", "2011_08_01", "2013_07_01"],
                        ], [
                            ["55908dfe9734042e6bbd4359", "2012_08_01", "2014_07_01"],
                        ], [
                            ["55908dfe9734042e6bbd4359", "2013_08_01", "2015_07_01"],
                        ]],
                                "features" : [["last_seven_results", "ranking", "day", "last_seven_goals", "last_seven_home_or_away", "last_seven_shots", "last_seven_goals_per_shots", "last_seven_rankings"]]
                                },
                   "algorithm" : {"name" : "nn",
                                  "params" : {"learning_rate" : [0.8], "momentum" : [0., 0.99]}},
                   "start_money" : [100.],
                   "percentage_bet" : [0.05],
                   "simult_bet" : [10]
                   }
    results = bulk_simulation(param)
    print results
    results = [param] + results
    filename = "test.pickle"
    pickle.dump(results, open(filename, "wb"))    
