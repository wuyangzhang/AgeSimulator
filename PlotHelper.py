import matplotlib.pyplot as plt
import numpy as np
import glob
import json
import collections

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

plt.rc('font', **font)

def plotSingleCurve(vals, xlabel = None, ylabel = None):
    x = [_ for _ in range(len(vals))]
    #plt.plot(x, vals)
    plt.plot(x, vals, color = '#9F353A')
    ax = plt.gca()
    ax.spines['left'].set_linestyle('-.')
    ax.spines['left'].set_color('#91989F')
    ax.spines['bottom'].set_linestyle('-.')
    ax.spines['bottom'].set_color('#91989F')

    ax.spines['right'].set_linestyle('--')
    ax.spines['right'].set_color('#91989F')
    ax.spines['top'].set_linestyle('--')
    ax.spines['top'].set_color('#91989F')

    ax.tick_params(axis='x', colors='#91989F')
    ax.tick_params(axis='y', colors='#91989F')

    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    plt.grid(linestyle='dotted')
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.show()



def plotAvgAOI(path, xticks = None, xlabel = None, ylabel = None):
    policyList = ('maxCarAgeDrop', 'FIFO', 'FCLS', 'minAge', 'maxAge', 'randomPick')
    with open(path) as f:
        aoi_policy_dic = json.load(f)

    # sort number
    keys = []
    others = [0] * 2
    for i, key in enumerate(aoi_policy_dic.keys()):
        res = key.split('_')
        keys.append(int(res[1]))
        others[0] = res[0]
        others[1] = res[2]

    keys.sort()
    vals = collections.defaultdict(list)

    for key in keys:
        tmp = others[:]
        tmp.insert(1, str(key))
        key = '_'.join(tmp)
        for policy in policyList:
            vals[policy].append(aoi_policy_dic[key][policy])


    x = [_  for _ in range(len(vals[policyList[0]]))]

    ax = plt.gca()
    ax.spines['left'].set_linestyle('-.')
    ax.spines['left'].set_color('#91989F')
    ax.spines['bottom'].set_linestyle('-.')
    ax.spines['bottom'].set_color('#91989F')

    ax.spines['right'].set_linestyle('--')
    ax.spines['right'].set_color('#91989F')
    ax.spines['top'].set_linestyle('--')
    ax.spines['top'].set_color('#91989F')

    ax.tick_params(axis='x', colors='#91989F')
    ax.tick_params(axis='y', colors='#91989F')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if xticks:
        plt.xticks(np.arange(6), xticks)
    plt.grid(linestyle='dotted')

    for policy in policyList:
        print(policy, vals[policy])
        plt.plot(x, vals[policy], label = policy)

    plt.legend(loc='upper left')

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)


    plt.show()

def plotSampleAge(path, xticks = None, xlabel = None, ylabel = None):

    with open(path) as f:
        aoi_list = json.load(f)



    ax = plt.gca()
    ax.spines['left'].set_linestyle('-.')
    ax.spines['left'].set_color('#91989F')
    ax.spines['bottom'].set_linestyle('-.')
    ax.spines['bottom'].set_color('#91989F')

    ax.spines['right'].set_linestyle('--')
    ax.spines['right'].set_color('#91989F')
    ax.spines['top'].set_linestyle('--')
    ax.spines['top'].set_color('#91989F')

    ax.tick_params(axis='x', colors='#91989F')
    ax.tick_params(axis='y', colors='#91989F')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    plt.grid(linestyle='dotted')

    for i, user in enumerate(aoi_list):
        user = user[:500]
        x = [_ for _ in range(len(user))]
        plt.plot(x, user, label = 'user #' + str(i))

    plt.legend(loc='upper left')

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)


    plt.show()


def plotBox(path, xlabel = None, ylabel = None):

    with open(path) as f:
        aoi_list = json.load(f)

    ax = plt.gca()
    ax.spines['left'].set_linestyle('-.')
    ax.spines['left'].set_color('#91989F')
    ax.spines['bottom'].set_linestyle('-.')
    ax.spines['bottom'].set_color('#91989F')

    ax.spines['right'].set_linestyle('--')
    ax.spines['right'].set_color('#91989F')
    ax.spines['top'].set_linestyle('--')
    ax.spines['top'].set_color('#91989F')

    ax.tick_params(axis='x', colors='#91989F')
    ax.tick_params(axis='y', colors='#91989F')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    #plt.grid(linestyle='dotted')


    fig = plt.figure(1, figsize=(9, 6))
    ax = fig.add_subplot(111)
    bp = ax.boxplot(aoi_list, showfliers=False)



    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)


    plt.show()



