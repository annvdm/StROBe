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

    def __init__(self, bui_names, bui_numbers, path, sample_time, filter=False, test=False, extra_name=None):
        """
        Simulate clusters of buildings

        :param bui_names: list of names of buildings or clusters to be simulated
        :param bui_numbers: number of buildings to be simulated per cluster
        :param path: path in which to store output files
        :param int sample_time: sample time between data points. Should be an integer multiple of 60 sec.
        :param bool filter: If True, profiles with a constant comfort temperature are removed from the output
        :param bool test: if True, suppress simulations to reduce runtime. Default False.
        :param str extra_name: provide name with which to save summary files. Default None
        """
        self.feeders = {}
        self.bui_numbers = bui_numbers
        self.buiNames = bui_names

        cdir = os.getcwd()

        for i, name in enumerate(bui_names):
            nbui = bui_numbers[i]
            print '\n---- Cluster %s ----' % name
            self.feeders[name] = IDEAS_Feeder(name=name, nBui=nbui, path=path, sample_time=sample_time, filter=filter, average=True, extra_name=True, cleanup=True, test=test)
            os.chdir(cdir)

        os.chdir(path)
        print '---- Combining clusters now ----'
        self.output(extra_name)

    def order_data(self):
        dat = {}

        for name in self.buiNames:
            feeder= self.feeders[name]
            print 'Name: {}'.format(name)
            for key in feeder.av:
                if key not in dat:
                    dat[key] = feeder.av[key]
                else:
                    dat[key] = np.vstack((dat[key], feeder.av[key]))

        return dat

    def output(self, extra_name):
        dat_dict = self.order_data()


        for key in dat_dict:
            tim = np.linspace(0, 31536000, dat_dict[key].shape[1])
            dat = dat_dict[key]
            #print '*** Data shape: {}'.format(dat_dict[key].shape[1])
            dat = np.vstack((tim, dat))

            # Data to txt
            hea = '#1\n//{} \ndouble data('.format(self.buiNames) + str(len(tim)) + ',' + str(len(self.bui_numbers) + 1) + ')'
            if extra_name is not None:
                filename = '{}_{}.txt'.format(extra_name, key)
            else:
                filename = '{}.txt'.format(key)

            np.savetxt(fname=filename, X=dat.T, header=hea, comments='')


class IDEAS_Feeder(object):
    """
    The Community class defines a set of households.
    """
    
    def __init__(self, name, nBui, path, sample_time, filter=False, average=False, extra_name=False, cleanup=False, test=False):
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

        if not test:
            for var in variables:
                self.output(var, sample_time, extra_name=extra_name)
        # and conclude

        if average:
            self.av = self.create_average_building(variables)
        else:
            av = None

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
        print dat[:, :10]
        #print '*** Complete data **************************'
        #print dat
        ratio = int(sample_time/60)
        new_len = int(len(var)/ratio)
        new_dat = np.zeros((dat.shape[0], new_len))

        if ratio == 1:
            new_dat=dat
        else:
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
            dat = np.loadtxt(fname='{}_{}.txt'.format(variable, self.name),skiprows=2, unpack=True)
            if not self.nBui == 1:
                new_dat[variable] = np.mean(dat[1:], axis=0)
            else:
                new_dat[variable] = dat[1]
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
