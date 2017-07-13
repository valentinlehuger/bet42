import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def list_of_list(data, name=None):
    if name is None:
        name = str(len(data))
    fig = plt.figure()
    fig.canvas.set_window_title(name)
    x = np.arange(0, len(data[0]), 1)
    for y in data:
        ax = fig.add_subplot(111)
        ax.plot(x, y, marker='.')
    fig.show()
    return fig

def bs_mean_stddev_mpcv(results, name=None):
    if name is None:
        name = "bs_mean_stddev_mpcv"
    means = dict()
    stddev = dict()
    for i in xrange(1, len(results)):
        if results[i]["parameter"]["dataset"]["src"][0][1][:4] not in means:
            means[results[i]["parameter"]["dataset"]["src"][0][1][:4]] = list()
            stddev[results[i]["parameter"]["dataset"]["src"][0][1][:4]] = list()
        means[results[i]["parameter"]["dataset"]["src"][0][1][:4]].append(results[i]["result"]["money_post_cross_validation"]["describe"]["mean"])
        stddev[results[i]["parameter"]["dataset"]["src"][0][1][:4]].append(results[i]["result"]["money_post_cross_validation"]["standard_deviation"])
    meansarr = np.empty((0, len(means[means.keys()[0]])), float)
    stddevarr = np.empty((0, len(means[means.keys()[0]])), float)
    years = list()
    for y in sorted(means.keys()):
        meansarr = np.append(meansarr, [means[y]], axis=0)
        stddevarr = np.append(stddevarr, [stddev[y]], axis=0)
        years.append(y)
    meanslst = list(list(sim_result_crossyear) for sim_result_crossyear in meansarr.T)
    stddevlst = list(list(sim_result_crossyear) for sim_result_crossyear in stddevarr.T)
    fig = plt.subplots()
    index = np.arange(len(means))
    margin = 0.
    bar_width = (2. - 2. * margin) / len(results)
    opacity = 0.4
    error_config = {"ecolor": "0.3"}
    for i in xrange(0, len(meanslst)):
        plt.bar(index + margin + i * bar_width, meanslst[i], bar_width, alpha=opacity, yerr=stddevlst[i], color=cm.jet(1.*i/len(meanslst)), error_kw=error_config, label="Sim" + str(i + 1))
    plt.xticks(index + bar_width, years)
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)
    return fig

if __name__ == "__main__":
    y = [np.arange(0, 10, 1), np.linspace(1, 10, 10)]
    list_of_list(y, "test_list_of_list")
    raw_input()
