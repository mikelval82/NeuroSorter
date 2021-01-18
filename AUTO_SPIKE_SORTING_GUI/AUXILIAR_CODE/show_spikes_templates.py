# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from decorators.time_consuming import timeit 

import numpy as np 
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import matplotlib
matplotlib.use('Qt5Agg')

@timeit
def run(spike_dict, current):

    mypath = './CLEANER/spike_templates/'
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    
    for file in files:
        plt.figure()  
        plt.plot(np.load(mypath+file), 'c', linewidth=4)
    plt.show()