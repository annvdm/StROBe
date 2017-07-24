#!/usr/bin/env python
"""
Description
"""
import numpy as np
from Corpus import stats

# From residential.py

types = dict()

# Added 4% chance of pattern one (no heating) to be representative for entire city
types.update({'1': {1: 12.0, 2: 12.0, 3: 12.0}})
types.update({'2': {1: 18.5, 2: 15.0, 3: 18.5}})
types.update({'3': {1: 20.0, 2: 15.0, 3: 19.5}})
types.update({'4': {1: 20.0, 2: 11.0, 3: 19.5}})
types.update({'5': {1: 20.0, 2: 14.5, 3: 15.0}})
types.update({'6': {1: 21.0, 2: 20.5, 3: 21.0}})
types.update({'7': {1: 21.5, 2: 15.5, 3: 21.5}})
# and the probabilities these types occur based on Duth research,
# i.e. Leidelmeijer and van Grieken (2005).
types.update({'prob': [0.04, 0.16, 0.35, 0.08, 0.11, 0.05, 0.20]})
# and given a type, denote which rooms are heated
given = dict()
given.update({'1': [['dayzone', 'bathroom', 'nightzone']]})
given.update({'2': [['dayzone', 'bathroom']]})
given.update({'3': [['dayzone'], ['dayzone', 'bathroom'], ['dayzone', 'nightzone']]})
given.update({'4': [['dayzone'], ['dayzone', 'nightzone']]})
given.update({'5': [['dayzone']]})
given.update({'6': [['dayzone', 'bathroom', 'nightzone']]})
given.update({'7': [['dayzone', 'bathroom']]})

#######################################################################
# select a type from the given tipes and probabilities
test = []
rooms = []
for i in range(1000000):
    rnd = np.random.random()
    shtype = str(stats.get_probability(rnd, types['prob'], 'prob'))
    test.append(int(shtype))
    if len(np.shape(given[shtype])) != 1:
        nr = np.random.randint(np.shape(given[shtype])[0])
        shrooms = given[shtype][nr]
        rooms.append(shrooms)
    else:
        shrooms = given[shtype]
        rooms.append(shrooms)

print test
#print rooms

import matplotlib.pyplot as plt
plt.hist(test, bins=[1,2,3,4,5,6,7,8], normed=True)
plt.show()