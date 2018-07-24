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
    """
    Take an average over all the columns of a dataframe

    :param data: A pandas.DataFrame object
    :return: A pandas.Series object containing the vaerage
    """
    return data.mean(axis=1)


def find_edges(df):
    """
    Finds the locations in a pandas.Series object where the value decreases

    :param df: pandas.Series object
    :return: List of index values where the corresponding value is about to decrease
    """
    edges = df.diff()[df.diff() < -10**-4].index.values

    return edges


def min_temp_profile(df, R, C, heat, tamb, start_time=pd.Timestamp('20140101')):
    """
    Calculates the actual minimum possible temperature profile for a building

    :param df: Minimum comfort temperature profile
    :param R: Resistance of the building [K/W]
    :param C: Capacitance of the building [J/kg/K]
    :param heat: Nominal heat that can be delivered to the building
    :param tamb: Ambient temperature
    :param start_time: Time from which the actual minimum temperature should be calculated
    :return:
    """

    df = df.copy()
    time_step = df.index[1] - df.index[0]  # Time step of the minimum temperature profile
    tamb = ut.resample(tamb, time_step)  # Resample ambien temperature to min. temp. profile's sampling time

    # Find the places where the comfort temperature decreases
    # From these points on the cooling down of the temperature on the building has to be calculated
    edges = find_edges(df)

    cool_down_flag = False  # Flag to indicate whether the building has cooled down to the minimum allowed temperature

    # Looping over all minimum temperatures
    for index, item in df.iteritems():
        if index in edges:
            # Building starts to cool down
            cool_down_flag = True
        if cool_down_flag:
            # Calculate new temperature after another time step of cooling down
            timeindex = start_time + pd.Timedelta(seconds=index)
            T_new = cool_down(df[index - time_step], tamb[timeindex], time_step, R*C)
            if T_new >= df[index]:
                # Temperature in the building has not cooled down yet to minimum allowed value
                    df[index] = T_new
            else:
                # Temperature in the building has cooled down to minimum allowed value
                cool_down_flag = False

    # Fing the places where the minimum comfort temperature increases
    # The dataframe is now reversed in direction, so a warm-up in the original dataframe is now a cool down again!
    # So code is the same as before!
    df = df.reindex(index=df.index[::-1])
    edges = find_edges(df)

    warm_up_flag = False
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
    """
    Average an minimum temperature profiles to a single profile

    Note: At the moment only a single type of building is possible (with only one R, C and nominal heat value possible)

    :param df: The dataframe containing all profiles (rows=time, columns=profiles)
    :param R: Average resistance of all buildings
    :param C: Average capacitance of all buildings
    :param heat: Average nominal heat that can be added to the buildings
    :param tamb: Ambient temperature profile
    :param start_time: Start time of the average minimum temperature profile
    :return:
    """

    # Calculate the minimum temperature profile for each building
    for column in df:
        df[column] = min_temp_profile(df[column], R, C, heat, tamb, start_time)

    return simple_average(df)


def cool_down(tstart, tamb, time_step, RC):
    """
    Method that calculates cool down of a building


    :param tstart: Start temperature of the building
    :param tamb: Ambient temperature during the considered time period
    :param time_step: Length of the time step during which the building is warmed up
    :param RC: RC value of the building
    :return: Temperature on the building at the end of the time ste[
    """
    return (tstart - tamb) * np.exp(-time_step / RC) + tamb


def warm_up(tstart, heat, time_step, C):
    """
    Method that calculates warm up of a building (in reverse direction! So starting from the warm temperature and
    calculating what the tenperature was in the time step before!)

    :param tstart: Start temperature of the building
    :param heat: Heat that is added to the building during the time step [W]
    :param time_step: Length of the time step during which the building is warmed up
    :param C: Capacity of the building
    :return:
    """
    return tstart - heat/C*time_step


def save_data(target_file, df):
    """
    Save the the dta to a Modelica-compatible format

    :param target_file:
    :param df:
    :return:
    """
    shape = (len(df.index), len(df.columns)+1)
    df.to_csv('tempfile.txt', header=None, sep=' ')
    header = '#1\ndouble data' + str(shape) + '\n'

    with open('tempfile.txt', 'r') as f:
        with open(target_file, 'w') as f2:
            f2.write(header)
            f2.write(f.read())
    os.remove('tempfile.txt')


def main():

    # Files of which a simple average can be taken
    simple_avg_files = ['mDHW', 'P', 'Q', 'QCon', 'QRad']

    # Files for zhich the min-temperature average algorithm should be used
    min_temp_files = ['sh_bath', 'sh_day', 'sh_night']

    # Information necessary to fond the StROBe files:
    building_types = ['D', 'SD', 'T']
    neighborhoods = ['TermienWest', 'TermienEast'] # , 'Boxbergheide', 'Winterslag', 'OudWinterslag', 'ZwartbergSouth',
                     # 'ZwartbergNWest', 'ZwartbergNWest', 'ZwartbergNEast', 'WaterscheiGarden'

    # Information on weather data, needed to calculate minimum temperature averages
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