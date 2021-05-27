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
import matplotlib
matplotlib.use('Qt5Agg')


@timeit
def run(spike_dict, current):
    colours = plt.get_cmap('Set1')     
    experiments = np.unique(spike_dict['ExperimentID'])

    for experiment in experiments:
        fs = spike_dict['SamplingRate'][experiment]
        waveforms = [spike_dict['Waveforms'][it] for it in current['plotted'] if spike_dict['ExperimentID'][it] == experiment]
        timestamps = [spike_dict['TimeStamps'][it] for it in current['plotted'] if spike_dict['ExperimentID'][it] == experiment]
        units = [spike_dict['UnitID'][it] for it in current['plotted'] if spike_dict['ExperimentID'][it] == experiment]

        plt.figure()
        for wave, stamp, unit in zip(waveforms, timestamps, units):
            point = np.argmin(wave)
            x = np.hstack( (np.arange(stamp-point,stamp), np.arange(stamp, stamp+len(wave)-point)) )
            plt.plot(x/fs, wave, color=colours(unit))
        
        if spike_dict['Triggers'][experiment]:
            for trigger in spike_dict['Trigger'][experiment]:
                 plt.axvline(x=trigger/fs, color='m')
            
        plt.show()
                
