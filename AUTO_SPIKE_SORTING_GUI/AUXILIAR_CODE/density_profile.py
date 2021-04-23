# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from decorators.time_consuming import timeit 

from seaborn import distplot
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')


@timeit
def run(spike_dict, current):
    ################ PARAMETERS TO ADJUST MANUALLY ##################
    experiment = 0

    ############### DO NOT CHANGE ANYTHING ########################
    
    fs = spike_dict['SamplingRate'][experiment]    
    timestamps = [spike_dict['TimeStamps'][it]/fs for it in current['plotted'] if spike_dict['ExperimentID'][it] == experiment]
    units = [spike_dict['UnitID'][it] for it in current['plotted'] if spike_dict['ExperimentID'][it] == experiment]       
    # Plotting
    plt.figure() 
    colours = plt.get_cmap('Set1') 
    for unit in np.unique(units):
        stamps = [stamp for it,stamp in enumerate(timestamps) if units[it] == unit]
        distplot(stamps, hist=False,  rug=True, kde_kws=dict(label="kde", color=colours(unit)), rug_kws=dict(height=.2, linewidth=2, color=colours(unit)))
    plt.xlabel('Time (s)')
    plt.ylabel(r'Density ($\sigma$)')
    plt.title('Probability Density function')
    plt.show()
