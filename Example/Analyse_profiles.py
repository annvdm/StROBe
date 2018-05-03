import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

nBui = 10

def readData(name):
    """
    Read neighborhood data and return as DataFrame

    :return pd.DataFrame: Neighborhood data DataFrame
    """
    filename = 'results/' + name + '.txt'

    data = pd.read_csv(os.path.abspath(filename), sep=' ', skiprows=[0,1], names=range(10))
    return data


def plot_data(name, duration):
    data = readData(name)

    sampling = data.index[1] - data.index[0]
    time_axis = pd.date_range('1/1/2018', periods=int(duration/sampling), freq=str(sampling) + 'S')

    fig, axarr = plt.subplots(nBui, sharex=True)
    for i in range(nBui):
        axarr[i].plot(time_axis, data[i][0:int(duration/sampling)])

    axarr[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(pd.date_range('1/1/2018', periods=int(duration/3600), freq='3600S'), rotation=90)
    fig.suptitle(name)

delta_t = 86400

plot_data('mDHW', delta_t)
plot_data('sh_day', delta_t)
plot_data('sh_bath', delta_t)
plot_data('sh_night', delta_t)


plt.show()