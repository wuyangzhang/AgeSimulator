import matplotlib.pyplot as plt
import numpy as np

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

    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    plt.grid(linestyle='dotted')
    plt.show()
