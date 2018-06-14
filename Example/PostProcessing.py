import os
import pandas as pd


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

    for neigh in neighborhoods:
        for name in simple_avg_files:
            df = pd.DataFrame(columns=building_types)
            for type in building_types:
                all_data = read_time_data(get_path(neigh, type), name + '.txt')
                df[type] = simple_average(all_data)

            save_data(os.path.join(get_path(neigh), name + '.txt'), df)


if __name__ == '__main__':
    main()