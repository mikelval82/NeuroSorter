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

    waveforms = []
    
    plt.figure()    
    for index in current['plotted']:
        plt.plot(spike_dict['Waveforms'][index], 'c')
        waveforms.append(spike_dict['Waveforms'][index])
    plt.plot( np.array(waveforms).mean(axis=0) , 'm')
    plt.show()
    mypath = './CLEANER/spike_templates/'
    numfiles = len([f for f in listdir(mypath) if isfile(join(mypath, f))])

    np.save(  './CLEANER/spike_templates/spike_template_' + str(numfiles) + '.npy', np.array(waveforms).mean(axis=0))
    
        
        
       