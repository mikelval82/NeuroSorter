#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 12:32:38 2020

@author: mikel
"""

import numpy as np 
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join

def run(spike_dict, current):

    mypath = './CLEANER/references/'
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    
    for file in files:
        plt.figure()  
        plt.plot(np.load(mypath+file), 'c', linewidth=4)
    plt.show()