#!/usr/bin/env python
"""
Description
"""
import os
import shutil
from collections import OrderedDict
from multiprocessing import Pool

import pandas as pd

import StROBe.Corpus.feeder as cf


def readData(path):
    """
    Read neighborhood data and return as DataFrame
    :return pd.DataFrame: Neighborhood data DataFrame
    """
    data = pd.read_csv(path, sep=' ')
    data = data.set_index('Neighborhood')
    return data


def getNeighbNames(data):
    """
    Return list of neighborhood names
    :param pd.DataFrame data: DataFrame with Neighborhood info
    :return list: list of neighborhood names
    """

    return data.index.values


def getNumbers(data, neighbname, buiType, maxNr=50):
    """
    Get numbers of neighborhoods
    :param data: Neighborhood data
    :param neighbname: Name of neighborhood
    :param buiType: 'D', 'SD' or 'T'
    :param max:  Maximal cluster size, default 50
    :return tuple: Name of neighborhood with type indication, number of buildings
    """

    assert buiType in ['D', 'SD', 'T'], 'Type must be D, SD or T'

    outName = "{}_{}".format(neighbname, buiType)

    # print data
    print 'buiType {}'.format(buiType)
    print 'neighbname {}'.format(buiType)
    number = data['Number' + str(buiType)][neighbname]
    outNumber = min(number, maxNr)
    print 'Number ' + str(outNumber)

    return outName, outNumber


def collecttxt(target, source=None):
    """
    Collect and save output files at an indicated location
    :param target: Target path where to copy txt files to
    :param source: Source location of files. If not supplied, current folder is taken (risky)
    :return:
    """
    if source is None:
        filedir = os.path.abspath('..')
    else:
        filedir = source
        os.chdir(source)

    names = [name for name in os.listdir(filedir) if os.path.isdir(os.path.join(filedir, name))]

    for name in names:
        foldir = os.path.join(filedir, name)
        # print foldir
        tocopy = [file for file in os.listdir(foldir) if (os.path.isfile(os.path.join(foldir, file)) and name in file)]
        # print tocopy
        for filename in tocopy:
            # print filename
            shutil.copy(os.path.join(foldir, filename), dst=target)
        print 'Copied results from {}'.format(name)


def makeStrobe(data):
    """
    Perform StROBe simulation for one neighborhood
    :param data: Dictionary with neighborhood and simulation data
    :return:
    """

    name = data['name']
    types = ['D', 'SD', 'T']

    parentpath = os.path.abspath('GenkNET/{}'.format(name))

    print '*** Path to save all files: {}'.format(parentpath)
    for buildingType in types:
        path = os.path.join(parentpath, buildingType)
        if not os.path.isdir(path):
            os.makedirs(path)
        cf.IDEAS_Feeder(name=buildingType, nBui=data[buildingType], path=path)


if __name__ == '__main__':

    ############################
    ##  PARAMETERS TO CHANGE  ##
    ############################

    multi = True  # Choose True to enable multiprocessing
    # part = 'Bram'  # or 'Annelies'
    proc = 3  # Number of simultaneous calculations

    source = os.path.abspath('GenkNET')
    # Where results of this file are saved (keep the Example/GenkNET structure, but change the rest accordingly)
    target = os.path.abspath('GenkNET')
    # Where the results should go (direct to subdirectory UserData of your GenkNET clone)

    ############################
    ##     CODE FROM HERE     ##
    ############################

    data_path = os.path.join(source, 'GenkNeighborhoods_test.txt')
    neighbdata = readData(data_path)
    names = getNeighbNames(neighbdata)[:2]
    # print neighbdata

    filepath = os.path.abspath(__file__)
    #os.chdir(os.path.dirname(filepath))
    #os.chdir('..')
    inputs = []

    for name in names:
        data = OrderedDict()
        for type in ['D', 'SD', 'T']:
            nametype, number = getNumbers(data=neighbdata, neighbname=name, buiType=type)
            data[type] = number
        data['name'] = name
        inputs.append(data)
        print("{: >20} {: >20} {: >20}".format(name, nametype, number))
    #
    if part == 'Bram':
        inputs = inputs[:4]
    else:
        inputs = inputs[5:]

    if multi:
        po = Pool(processes=proc)
        po.map(makeStrobe, inputs)
    else:
        for inp in inputs:
            makeStrobe(inp)

    if not os.path.isdir(target):
        os.mkdir(target)
    collecttxt(target, source)
