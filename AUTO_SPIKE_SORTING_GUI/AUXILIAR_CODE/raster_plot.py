# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
import numpy as np 
import matplotlib.pyplot as plt

def run(spike_dict, current):
    fs = 30000
    experiments = np.unique(spike_dict['ExperimentID'])
    print(experiments)
    for experiment in experiments:
        
        channels = np.unique([ch for it, ch in enumerate(spike_dict['ChannelID']) if spike_dict['ExperimentID'][it] == experiment])
    
        plt.figure()
        for channel in channels:
            index_ch= [it for it, ch in enumerate(spike_dict['ChannelID']) if ch == channel and spike_dict['ExperimentID'][it] == experiment and spike_dict['UnitID'][it] > 0]
            time_ch=np.array(spike_dict['TimeStamps'])[index_ch]/fs
        
            if len(time_ch>0):
                plt.plot(time_ch, np.transpose(channel*np.ones([1,len(time_ch)])),'|b')
            
        plt.xlabel('Time[s]')
        plt.ylabel('Channel')  
        plt.show()
