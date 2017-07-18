# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 11:39:35 2014

@author: Ruben
"""

import residential
import cPickle
import numpy as np
import os

class IDEAS_Feeder(object):
    """
    The Community class defines a set of households.
    """
    
    def __init__(self, name, nBui, path, sample_time, filter=False, average=False):
        """
        Create the community based on number of households and simulate for
        output towards IDEAS model.
        :param name: Name of the feeder
        :param nBui: Number of strobe profiles to be generated
        :param path: Path to folder where results are stored
        :param sample_time: Sample time of the profiles, in seconds
        :param filter: If True, profiles with a constant comfort temperature ae removed fro; the output
        :param average: If True, an average for the group of buildings is calculated and included as the last building in the output file
        """
        self.name = name
        self.nBui = nBui
        # we create, simulate and pickle all 'nBui' buildings
        self.simulate(path)
        # then we loop through all variables and output as single file
        # for reading in IDEAS.mo
        os.chdir(path)
        variables = ['P','Q','QRad','QCon','mDHW','sh_day','sh_bath','sh_night']


        # Filter out buildings that have a constant comfort temperature
        if filter:
            bui = self.filter()
        else:
            bui = range(self.nBui)

        if average:
            av = self.create_average_building(bui, variables)
        else:
            av = None

        for var in variables:
            self.output(bui, var, sample_time, filter=filter, average=av)
        # and conclude
        print '\n'
        print ' - Feeder %s outputted %s buildings.' % (str(self.name), len(bui))
        if average:
            '   Along with average building'

    def simulate(self, path):
        '''
        Simulate all households in the depicted feeder
        '''
        #######################################################################
        # we loop through all households for creation, simulation and pickling.
        # whereas the output is done later-on.
        cwd = os.getcwd()
        for i in range(self.nBui):
            hou = residential.Household(str(self.name)+'_'+str(i))
            hou.simulate()
            hou.roundUp()
            os.chdir(path)
            hou.pickle()
            os.chdir(cwd)

    def output(self, buildings, variable, sample_time, filter=False, average=None):
        '''
        Output the variable for the dwellings in the feeder as a *.txt readable
        for Modelica.
        '''
        #######################################################################
        # we loop through all households for loading the depicted variable data
        # which is stored in the object pickle.
        print '\nOutput ' + variable

        dat = np.zeros(0)
        for i in buildings:
            hou = cPickle.load(open(str(self.name)+'_'+str(i)+'.p','rb'))
            var = eval('hou.'+variable)
            if len(dat) != 0:
                dat = np.vstack((dat,var))
            else:
                dat = var

        if average[variable] is not None:
            dat = np.vstack((dat, average[variable]))

        #######################################################################
        # and output the array to txt
        assert var is not None, 'No buildings came out of the filter, please try again'
        tim = np.linspace(0, 31536000, len(var))
        dat = np.vstack((tim, dat))

        print 'Resampling data...'
        ratio = int(sample_time/(tim[1]-tim[0]))
        new_len = int(len(var)/ratio)
        new_dat = np.zeros((dat.shape[0], new_len))
        for k in range(int(len(var)/ratio)):
            new_dat[:, k] = np.mean(dat[:, ratio*k:ratio*(k+1)-1], axis=1)
            new_dat[0, k] = k*sample_time

        # Data to txt
        print 'Setting data in text'
        hea ='#1 \n double data('+str(int(len(var)))+','+str(self.nBui+1)+')'
        np.savetxt(fname=variable+'.txt', X=new_dat.T, header=hea)

    def filter(self):
        """
        Filter out the buildings that have a constant day confort temperature of 12 degrees
        :return: The list of buildings not filtered out
        """
        print '\nFiltering...'
        bui = []
        for i in range(self.nBui):
            hou = cPickle.load(open(str(self.name) + '_' + str(i) + '.p', 'rb'))
            var = eval('hou.sh_day')
            flag = False
            for val in var:
                if val != 12:
                    flag = True

            if flag:
                bui.append(i)

        return bui

    def create_average_building(self, buildings, variables):
        new_dat = {}
        for variable in variables:
            print variable
            dat = np.zeros(0)
            for i in buildings:
                hou = cPickle.load(open(str(self.name) + '_' + str(i) + '.p', 'rb'))
                var = eval('hou.' + variable)
                if len(dat) != 0:
                    dat = np.vstack((dat, var))
                else:
                    dat = var
            if 'sh' in variable:
                new_dat[variable] = np.mean(dat[:, :], axis=0)
            else:
                new_dat[variable] = len(buildings)*np.mean(dat[:, :], axis=0)

        return new_dat