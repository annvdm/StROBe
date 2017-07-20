#!/usr/bin/env python
"""
Description
"""
from collections import OrderedDict
import os
import pandas as pd

import Corpus.feeder


# Corpus.feeder.IDEAS_cluster()

def readData():
    """
    Read neighborhood data and return as DataFrame

    :return pd.DataFrame: Neighborhood data DataFrame
    """
    data = pd.read_csv('GenkNET/GenkNeighborhoods.txt', sep=' ')
    data = data.set_index('Neighborhood')
    return data


def getNeighbNames(data):
    """
    Return list of neighborhood names

    :param pd.DataFrame data: DataFrame with Neighborhood info

    :return list: list of neighborhood names
    """

    return data.index.values


def getNumbers(data, neighbname, type, maxNr=50):
    """
    Get numbers of neighborhoods

    :param data: Neighborhood data
    :param neighbname: Name of neighborhood
    :param type: 'D', 'SD' or 'T'
    :param max:  Maximal cluster size, default 50
    :return tuple: Name of neighborhood with type indication, number of buildings
    """

    assert type in ['D', 'SD', 'T'], 'Type must be D, SD or T'

    outName = "{}_{}".format(neighbname, type)
    number = data['Number{}'.format(type)][neighbname]
    outNumber = min(number, maxNr)

    return outName, outNumber


if __name__ == '__main__':
    neighbdata = readData()
    names = getNeighbNames(neighbdata)

    # print neighbdata

    filepath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(filepath))
    os.chdir('..')
    print os.getcwd()

    numbers = OrderedDict()

    for type in ['D', 'SD', 'T']:
        for name in names:
            nametype, number = getNumbers(neighbdata, name, type)
            numbers[nametype] = number
            print("{: >20} {: >20}".format(nametype, n))

    nametypes = numbers.keys()
    finalnumbers = [numbers[i] for i in nametypes]

    print 'Results saved in {}'.format(os.path.abspath('Example/GenkNET'))

    Corpus.feeder.IDEAS_feeder(nametypes, finalnumbers, os.path.abspath('Example/GenkNET'), 900, filter=True)
