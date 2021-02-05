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
    fs = spike_dict['SamplingRate']    
    colours = plt.get_cmap('Set1') 
    
    channelMap = np.array([None, 1,2,3,4,5,6,7,8,None,
                        9,10,11,12,13,14,15,16,17,18,
                        19,20,21,22,23,24,25,26,27,28,
                        29,30,31,32,33,34,35,36,37,38,
                        39,40,41,42,43,44,45,46,47,48,
                        49,50,51,52,53,54,55,56,57,58,
                        59,60,61,62,63,64,65,66,67,68,
                        69,70,71,72,73,74,75,76,77,78,
                        79,80,81,82,83,84,85,86,87,88,
                        None,89,90,91,92,93,94,95,96,None])
    
    electrodeMap = np.array([None,95,32,30,28,26,24,22,18,None,
                            96,63,61,64,31,29,27,20,16,14,
                            93,94,59,60,62,21,25,23,12,10,
                            92,91,57,58,52,54,19,13,11,8,
                            90,89,55,56,46,50,15,17,9,6,
                            88,87,53,51,44,42,48,5,7,4,
                            85,86,49,47,43,40,38,36,34,3,
                            83,84,82,45,41,39,37,35,33,1,
                            81,80,78,76,74,72,70,68,66,2,
                            None,79,77,75,73,71,69,67,65,None])
        
    experiments = np.unique(spike_dict['ExperimentID'])

    for experiment in experiments:

        fig = plt.figure()
        for channel in range(1,97):
            index = [it for it, channelID in enumerate(spike_dict['ChannelID']) if channelID == channel and spike_dict['ExperimentID'][it] == experiment and spike_dict['UnitID'][it] > -1]
            timestamps = [spike_dict['TimeStamps'][it]/fs for it in index]
            units = [spike_dict['UnitID'][it] for it in index]       

            idx = [idx for idx,ch in enumerate(channelMap) if ch == channel][0]
        
            plt.subplot(10, 10, idx+1)
            for unit in np.unique(units):
                stamps = [stamp for it,stamp in enumerate(timestamps) if units[it] == unit]
                if len(stamps) > 1:
                    distplot(stamps, hist=False,  rug=True)
    
            plt.axis('off')
            plt.title('E'+str(electrodeMap[idx])+'CH'+str(channelMap[idx]))
        fig.tight_layout()
        plt.show()
