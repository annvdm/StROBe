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
    '''
    The Community class defines a set of hosueholds.
    '''
    
    def __init__(self, name, nBui, path, sample_time):
        '''
        Create the community based on number of households and simulate for
        output towards IDEAS model.
        '''
        self.name = name
        self.nBui = nBui
        # we create, simulate and pickle all 'nBui' buildings
        self.simulate(path)
        # then we loop through all variables and output as single file
        # for reading in IDEAS.mo
        os.chdir(path)
        variables = ['P','Q','QRad','QCon','mDHW','sh_day','sh_bath','sh_night']
        for var in variables:
            self.output(var, sample_time)
        # and conclude
        print '\n'
        print ' - Feeder %s outputted.' % str(self.name)

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

    def output(self, variable, sample_time):
        '''
        Output the variable for the dwellings in the feeder as a *.txt readable
        for Modelica.
        '''
        #######################################################################
        # we loop through all households for loading the depicted variable data
        # which is stored in the object pickle.
        dat = np.zeros(0)
        for i in range(self.nBui):
            hou = cPickle.load(open(str(self.name)+'_'+str(i)+'.p','rb'))
            var = eval('hou.'+variable)
            if len(dat) != 0:
                dat = np.vstack((dat,var))
            else:
                dat = var
        #######################################################################
        # and output the array to txt
        tim = np.linspace(0, 31536000, len(var))
        dat = np.vstack((tim, dat))

        # Resampling
        ratio = int(sample_time/(tim[1]-tim[0]))
        new_len = int(len(var)/ratio)
        new_dat = np.zeros((dat.shape[0], new_len))
        for k in range(int(len(var)/ratio)):
            new_dat[:, k] = np.mean(dat[:, ratio*k:ratio*(k+1)-1], axis=1)
            new_dat[0, k] = k*sample_time

        # Data to txt
        hea ='#1 \n double data('+str(int(len(var)))+','+str(self.nBui+1)+')'
        np.savetxt(fname=variable+'.txt', X=new_dat.T, header=hea)

