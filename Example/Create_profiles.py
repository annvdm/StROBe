#!/usr/bin/env python
"""
Description
"""
import os
import matplotlib.pyplot as plt
import shutil
from collections import OrderedDict
from multiprocessing import Pool

import pandas as pd

import Corpus.feeder


# Corpus.feeder.IDEAS_cluster()

def readData(name):
    """
    Read neighborhood data and return as DataFrame

    :return pd.DataFrame: Neighborhood data DataFrame
    """
    filename = 'results/' + name + '.txt'

    data = pd.read_csv(os.path.abspath(filename), sep=' ', skiprows=[0,1], names=range(10))

    return data

def plot_data(name):
    data = readData(name)

    fig, ax = plt.subplots()
    ax.plot(data)


dir_path = os.path.dirname(os.path.realpath(__file__))
destination = os.path.join(dir_path, 'results')
if not os.path.isdir(destination):
    os.mkdir(destination)
# Corpus.feeder.IDEAS_Feeder('test', 10, destination)

plot_data('P')
plt.show()

# if __name__ == '__main__':
#
#     ############################
#     ##  PARAMETERS TO CHANGE  ##
#     ############################
#
#     multi = True  # Choose True to enable multiprocessing
#     part = 'Bram'  # or 'Annelies'
#     proc = 3  # Number of simultaneous calculations
#     homefolder = 'C:/Users/u0094934/Software/StROBe'
#     # CHANGE TO YOUR OWN StROBe DIRECTORY!
#
#     source = 'C:/Users/u0094934/Software/StROBe/Example/GenkNET'
#     # Where results of this file are saved (keep the Example/GenkNET structure, but change the rest accordingly)
#     target = 'C:/Users/u0094934/Documents/Dymola/GenkNET/UserData'
#     # Where the results should go (direct to subdirectory UserData of your GenkNET clone)
#
#     ############################
#     ##     CODE FROM HERE     ##
#     ############################
#
#     neighbdata = readData()
#     names = getNeighbNames(neighbdata)
#     # print neighbdata
#
#     filepath = os.path.abspath(__file__)
#     os.chdir(os.path.dirname(filepath))
#     os.chdir('..')
#     print os.getcwd()
#
#     inputs = []
#
#     for name in names:
#         data = OrderedDict()
#         for type in ['D', 'SD', 'T']:
#             nametype, number = getNumbers(data=neighbdata, neighbname=name, buiType=type)
#             data[type] = number
#         data['name'] = name
#         data['home'] = homefolder
#         inputs.append(data)
#         print("{: >20} {: >20} {: >20}".format(name, nametype, number))
#
#     if part == 'Bram':
#         inputs = inputs[:4]
#     else:
#         inputs = inputs[5:]
#     print inputs
#
#     if multi:
#         po = Pool(processes=proc)
#         po.map(makeStrobe, inputs)
#     else:
#         for inp in inputs:
#             makeStrobe(inp)
#
#
#     if not os.path.isdir(target):
#         os.mkdir(target)
#     collecttxt(target, source)
