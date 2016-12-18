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
resultpath = os.path.abspath('Example\\testFeederOut')
print 'Results saved in: '+resultpath

if not os.path.isdir(resultpath):
    os.mkdir(resultpath)

test = Corpus.feeder.IDEAS_Feeder('test', 1, resultpath)
