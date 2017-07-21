#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File to test the behaviour of feeder.IDEAS_Cluster()

Output of script:
In subfolder Example/testClusterOut txt files are saved:
Txt-files named: <<var>>_<<cluster_name>>: contain all data of buildings in one cluster
Txt-files named: <<var>>: contain all aggregated data of all clusters, ordered in alphabetical order

"""
import os
import Corpus.feeder

filepath = os.path.abspath(__file__)
os.chdir(os.path.dirname(filepath))
os.chdir('..')
print os.getcwd()

# Replace this
resultpath = os.path.abspath('Example\\testClusterOut')
print 'Results saved in: '+resultpath

if not os.path.isdir(resultpath):
    os.mkdir(resultpath)

test = Corpus.feeder.IDEAS_cluster(['haarHakker', 'peterslei'], [2, 1], resultpath, sample_time=900, filter=False)
