from __future__ import division
import os
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import modesto.utils as ut
from pkg_resources import resource_filename

def get_path(neighborhood, b_type=None):
    """
    Load data belonging to one neighborhood and type of building

    :param neighborhood: Neighborhood name
    :param b_type: Building type
    :return:
    """

    source = os.path.abspath('GenkNET')
    if b_type is None:
        path = os.path.join(source, neighborhood)
    else:
        path = os.path.join(source, neighborhood, b_type)

    if not os.path.isdir(path):
        raise Exception('No data exists for neighborhood {}, building type {}'.format(neighborhood, type))

    return path


def read_file(path, name, timestamp):
    """
    Read a text file and return it as a dataframe

    :param path: Location of the file
    :param name: name of the file (add extension)
    :param timestamp: if data contains a timestamp column. Default True
    :return: A dataframe
    """

    fname = os.path.join(path, name)

    if not os.path.isfile(fname):
        raise IOError(fname + ' does not exist')

    data = pd.read_csv(fname, sep=' ', header=None,
                       index_col=0, skiprows=2)

    return data


def read_time_data(path, name, expand=False, expand_year=2014):
    """
    Read a file that contains time data,
    first column should contain strings representing time in following format:
    %Y-%m-%d  %H:%M:%S
    And each column should have a title

    :param path: Location of the file
    :param name: name of the file (add extension)
    :param expand: Boolean. Decides if data should wrap around itself such that optimizations at the very beginning or end of the year can be performed. Default False.
    :param expand_year: if expand=True, which year should be padded. All other data is removed. Default 2014.
    :return: A dataframe
    """

    df = read_file(path, name, timestamp=True)
    df = df.astype('float')

    assert isinstance(expand_year, int), 'Integer is expected for expand_year.'

    if expand:
        df = expand_df(df, expand_year)

    return df


def expand_df(df, start_year=2014):
    """
    Pad a given data frame with data for one year with a month of data for the previous and next year. The first and last month are repeated respectively.

    :param df: input dataframe or series
    :param start_year: Year that should be padded.
    :return:
    """

    data = df[df.index.year == start_year]
    before = data[data.index.month == 12]
    before.index = before.index - pd.DateOffset(years=1)

    after = data[data.index.month == 1]
    after.index = after.index + pd.DateOffset(years=1)

    return pd.concat([before, data, after])


def simple_average(data):
    return data.mean(axis=1)


def find_edges(df):
    edges = df.diff()[df.diff() < -10**-4].index.values

    return edges


def min_temp_profile(df, R, C, heat, tamb, start_time=pd.Timestamp('20140101')):
    df = df.copy()
    time_step = df.index[1] - df.index[0]
    tamb = ut.resample(tamb, time_step)

    edges = find_edges(df)

    cool_down_flag = False
    for index, item in df.iteritems():
        if index in edges:
            cool_down_flag = True
        if cool_down_flag:
            timeindex = start_time + pd.Timedelta(seconds=index)
            T_new = cool_down(df[index - time_step], tamb[timeindex], time_step, R*C)
            if T_new >= df[index]:
                    df[index] = T_new
            else:
                cool_down_flag = False

    df = df.reindex(index=df.index[::-1])

    warm_up_flag = False
    edges = find_edges(df)
    for index, item in df.iteritems():
        if index in edges:
            warm_up_flag = True
        if warm_up_flag:
            T_new = warm_up(df[index+time_step], heat, time_step, C)
            if T_new >= df[index]:
                    df[index] = T_new
            else:
                warm_up_flag = False

    df = df.reindex(index=df.index[::-1])
    return df


def min_temp_average(df, R, C, heat, tamb, start_time=pd.Timestamp('20140101')):
    for column in df:
        df[column] = min_temp_profile(df[column], R, C, heat, tamb, start_time)

    return simple_average(df)


def cool_down(tstart, tamb, time_step, RC):
    return (tstart - tamb) * np.exp(-time_step / RC) + tamb


def warm_up(tstart, heat, time_step, C):
    return tstart - heat/C*time_step


def save_data(target_file, df):
    shape = (len(df.index), len(df.columns)+1)
    df.to_csv('tempfile.txt', header=None, sep=' ')
    header = '#1\ndouble data' + str(shape) + '\n'

    with open('tempfile.txt', 'r') as f:
        with open(target_file, 'w') as f2:
            f2.write(header)
            f2.write(f.read())
    os.remove('tempfile.txt')


def main():
    simple_avg_files = ['mDHW', 'P', 'Q', 'QCon', 'QRad']
    min_temp_files = ['sh_bath', 'sh_day', 'sh_night']
    building_types = ['D', 'SD', 'T']
    neighborhoods = ['TermienWest', 'TermienEast'] # , 'Boxbergheide', 'Winterslag', 'OudWinterslag', 'ZwartbergSouth',
                     # 'ZwartbergNWest', 'ZwartbergNWest', 'ZwartbergNEast', 'WaterscheiGarden'

    datapath = resource_filename('modesto', 'Data')
    tamb = ut.read_time_data(datapath, name='Weather/weatherData.csv', expand=True)['Te']

    for neigh in neighborhoods:
        print '\n', neigh
        print '-------------------'
        for name in simple_avg_files + min_temp_files:
            print '\n', name + '.txt'
            df = pd.DataFrame(columns=building_types)
            for b_type in building_types:
                print b_type
                all_data = read_time_data(get_path(neigh, b_type), name + '.txt')
                if name in simple_avg_files:
                    df[b_type] = simple_average(all_data)
                else:
                    # TODO Add good building model and parameters!
                    df[b_type] = min_temp_average(all_data, 0.5, 1000000, 10, tamb - 273.15)

            save_data(os.path.join(get_path(neigh), name + '.txt'), df)


if __name__ == '__main__':
    main()