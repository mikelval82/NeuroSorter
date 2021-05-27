#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 10:21:09 2021

@author: mikel
"""

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
    #------------ PARAMETERS TO BE SET BY USERS ----------------------------------------#########################
    experiment = 0        
    reference_channel = 18  
    reference_unit = 1   
    channel = 32
    unit =  1     
    bin_width = 100     
    range_ = np.array([-1,1])               
    #------------ DO NOT CHANGE ANYTHING ----------------------------------------#############################
    fs = int(spike_dict['SamplingRate'][experiment])
    trigger_timestamps = np.array([spike_dict['TimeStamps'][it] for it,ch in enumerate(spike_dict['ChannelID']) if ch == reference_channel and spike_dict['UnitID'][it] == reference_unit and spike_dict['ExperimentID'][it] == experiment])/fs
    unit_timestamps = np.array([spike_dict['TimeStamps'][it] for it,ch in enumerate(spike_dict['ChannelID']) if ch == channel and spike_dict['UnitID'][it] == unit and spike_dict['ExperimentID'][it] == experiment])/fs
    
    datahist = []
    for trigger_stamp in trigger_timestamps:	
        datahist = datahist + [(stamp - trigger_stamp) for stamp in unit_timestamps if stamp > trigger_stamp+range_[0] and stamp < trigger_stamp+ range_[1]]
        
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.hist(datahist, bins=bin_width) 
    ax1.axvline(x=0, color='m', linewidth=3)
        
    ax1.set_xlim(left=range_[0], right=range_[1])
    ax1.set_ylabel('Count',fontsize=16)
    ax1.set_title('Peristimulus\nChannel {0}, n = {1} trials'.format(reference_channel, len(trigger_timestamps)))
    
    ax2 = fig.add_subplot(212)
    for i in range(trigger_timestamps.size - 1):
        trial_raster = [(stamp - trigger_timestamps[i]) for stamp in unit_timestamps if stamp > trigger_timestamps[i]+range_[0] and stamp < trigger_timestamps[i]+ range_[1]]
        ax2.plot(trial_raster, np.transpose(i*np.ones([1,len(trial_raster)])),'|b')
    
    ax2.set_xlim(left=range_[0], right=range_[1])
    ax2.set_xlabel('Trial Window, s',fontsize=16)
    ax2.set_ylabel('Trial Number',fontsize=16)
    ax2.set_title('Raster\nChannel {0}, n = {1} trials'.format( reference_channel, len(trigger_timestamps) ))
    plt.show()
                        
                        
                        

