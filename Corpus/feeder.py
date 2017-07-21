# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 11:39:35 2014

@author: Ruben
"""

from __future__ import division
import residential
import cPickle
import numpy as np
import os



class IDEAS_cluster:

    def __init__(self, bui_names, bui_numbers, path, sample_time, filter=False):
        """
        Simulate clusters of buildings

        :param bui_names: list of names of buildings or clusters to be simulated
        :param bui_numbers: number of buildings to be simulated per cluster
        :param path: path in which to store output files
        :param sample_time: sample time between data points
        :param filter: If True, profiles with a constant comfort temperature are removed from the output
        """
        self.feeders = {}
        self.bui_numbers = bui_numbers
        self.buiNames = bui_names

        cdir = os.getcwd()

        for i, name in enumerate(bui_names):
            nbui = bui_numbers[i]
            print '\n---- Cluster %s ----' % name
            self.feeders[name] = IDEAS_Feeder(name=name, nBui=nbui, path=path, sample_time=sample_time, filter=filter, average=True, extra_name=True, cleanup=False)
            os.chdir(cdir)

        os.chdir(path)
        print '---- Combining clusters now ----'
        self.output(sample_time, self.order_data())

    def order_data(self):
        dat = {}

        for name, feeder in self.feeders.items():
            for key in feeder.av:
                if key not in dat:
                    dat[key] = feeder.av[key]
                else:
                    dat[key] = np.vstack((dat[key], feeder.av[key]))

        for key in dat:
            print '{}: {}'.format(key, dat[key].shape)
        return dat

    def output(self, sample_time, dat_dict):
        for key, dat in dat_dict.items():
            tim = np.linspace(0, 31536000, dat.shape[1])
            dat = np.vstack((tim, dat))

            ratio = int(sample_time / (tim[1] - tim[0]))
            print '{} - Ratio: {}'.format(key, ratio)
            new_len = int(len(tim) / ratio)
            new_dat = np.zeros((dat.shape[0], new_len))

            if "sh" in key:
                print 'tim:     {}'.format(tim)
                print 'new_len: {}'.format(new_len)
            for k in range(int(len(tim) / ratio)):
                logfile.write('{} \n'.format(str(dat[:, ratio * k:ratio * (k + 1) - 1])))
                new_dat[:, k] = np.mean(dat[:, ratio * k:ratio * (k + 1) - 1], axis=1)
                new_dat[0, k] = k * sample_time

            # Data to txt
            hea = '#1 \ndouble data(' + str(int(new_len)) + ',' + str(len(self.bui_numbers) + 1) + ')'

            np.savetxt(fname=key + '.txt', X=new_dat.T, header=hea, comments='')


class IDEAS_Feeder(object):
    """
    The Community class defines a set of households.
    """
    
    def __init__(self, name, nBui, path, sample_time, filter=False, average=False, extra_name=False, cleanup=False, test=True):
        """
        Create the community based on number of households and simulate for
        output towards IDEAS model.
        

        :param name: Name of the feeder
        :param nBui: Number of strobe profiles to be generated
        :param path: Path to folder where results are stored
        :param sample_time: Sample time of the profiles, in seconds
        :param filter: If True, profiles with a constant comfort temperature are removed from the output
        :param average: If True, an average for the group of buildings is calculated and included as the last building in the output file
        :param extra_name: If True, the name of the set of households is included in the name of output txt files
        :param cleanup: True if .p files should be removed
        :param test: True if simulation should not be run to make testing faster
        """
        self.name = name
        self.nBui = nBui
        self.bui = range(nBui)
        # we create, simulate and pickle all 'nBui' buildings
        if not test:
            self.simulate(path, filter)
        # then we loop through all variables and output as single file
        # for reading in IDEAS.mo
        os.chdir(path)
        variables = ['P', 'Q', 'QRad', 'QCon', 'mDHW', 'sh_day', 'sh_bath', 'sh_night']



        if average:
            self.av = self.create_average_building(variables)
        else:
            av = None

        for var in variables:
            self.output(var, sample_time, extra_name=extra_name)
        # and conclude
        print '\n'
        print ' - Feeder %s outputted %s buildings.' % (str(self.name), nBui)
        if average:
            print '   Along with average building'
        if cleanup:
            self.cleanup()

    def simulate(self, path, filter):
        '''
        Simulate all households in the depicted feeder
        '''
        #######################################################################
        # we loop through all households for creation, simulation and pickling.
        # whereas the output is done later-on.
        cwd = os.getcwd()
        for i in self.bui:
            hou = residential.Household(str(self.name)+'_'+str(i))
            if filter:
                flag = False
                while not flag:
                    hou.simulate()
                    flag = hou.roundUp()
                    if not flag:
                        print 'Building is removed, a new one is made'
            else:
                hou.simulate()
                hou.roundUp()
            os.chdir(path)
            hou.pickle()
            os.chdir(cwd)

    def output(self, variable, sample_time, extra_name=False):
        '''
        Output the variable for the dwellings in the feeder as a *.txt readable
        for Modelica.
        '''
        #######################################################################
        # we loop through all households for loading the depicted variable data
        # which is stored in the object pickle.
        print 'Output ' + variable
        dat = np.zeros(0)
        for i in self.bui:
            hou = cPickle.load(open(str(self.name) + '_' + str(i) + '.p', 'rb'))
            var = eval('hou.' + variable)
            # If data is given every 10 minutes, repeat every 1 minute
            if len(var) == 52561:
                var = np.repeat(var, 10)
                # now var has 9 elements too many, so delete them
                var = var[:len(var)-9]
            if len(dat) != 0:
                dat = np.vstack((dat, var))
            else:
                dat = var
        #print 'Length of var {}: {}'.format(variable, len(var))
        #######################################################################
        # and output the array to txt
        tim = np.linspace(0, 31536000, len(var))
        dat = np.vstack((tim, dat))
        #print '*** Complete data **************************'
        #print dat
        ratio = int(sample_time/60)
        new_len = int(len(var)/ratio)+1
        new_dat = np.zeros((dat.shape[0], new_len))

        for k in range(new_len):
            new_dat[:, k] = np.mean(dat[:, ratio*k:ratio*(k+1)-1], axis=1)
            new_dat[0, k] = k*sample_time

        # Data to txt
        hea ='#1 \ndouble data('+str(int(new_len))+','+str(self.nBui+1)+')'

        if extra_name:
            name = variable + '_' + self.name
        else:
            name = variable

        np.savetxt(fname=name+'.txt', X=new_dat.T, header=hea, comments='')

    def create_average_building(self, variables):
        new_dat = {}
        for variable in variables:
            dat = np.zeros(0)
            for i in self.bui:
                hou = cPickle.load(open(str(self.name) + '_' + str(i) + '.p', 'rb'))
                var = eval('hou.' + variable)
                if len(dat) != 0:
                    dat = np.vstack((dat, var))
                else:
                    dat = var
            if not self.nBui == 1:
                new_dat[variable] = np.mean(dat, axis=0)
            else:
                new_dat[variable] = dat

        return new_dat

    def cleanup(self):
        """
        Clean all pickle files of this feeder from working directory

        :return:
        """
        filelist = [ f for f in os.listdir(".") if (f.endswith(".p") and f.startswith(str(self.name)))]
        for f in filelist:
            os.remove(f)
        print '   .p files removed.'
