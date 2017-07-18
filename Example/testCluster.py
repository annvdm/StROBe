#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File to test the behaviour of feeder.IDEAS_Feeder()
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

test = Corpus.feeder.IDEAS_cluster({'haarHakker': 2, 'peterslei': 1}, resultpath, 3600, filter=False)
