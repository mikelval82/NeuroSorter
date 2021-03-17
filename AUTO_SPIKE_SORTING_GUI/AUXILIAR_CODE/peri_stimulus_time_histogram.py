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
    channel = 56                                   
    trigger = 0                                       
    unit =  2#'all'                                       
    bin_width = 100                              
    range_ = np.array([-.3,1])               
    #------------ DO NOT CHANGE ANYTHING ----------------------------------------#########################
    if unit == 'all':
        TimeStamps = [spike_dict['TimeStamps'][it] for it,ch in enumerate(spike_dict['ChannelID']) if spike_dict['ExperimentID'][it] == experiment and ch == channel and spike_dict['UnitID'][it] != -1]
    else:
        TimeStamps = [spike_dict['TimeStamps'][it] for it,ch in enumerate(spike_dict['ChannelID']) if spike_dict['ExperimentID'][it] == experiment and ch == channel and spike_dict['UnitID'][it] == unit]

    fs = int(spike_dict['SamplingRate'][experiment]  )
    triggers = spike_dict['Triggers'][experiment][trigger]
    
    datahist = []
    for i in range(len(triggers) - 1):
        datahist = datahist + [(stamp - triggers[i])/fs for stamp in TimeStamps if stamp > triggers[i]+range_[0]*fs and stamp < triggers[i]+ range_[1]*fs]
        
    
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.hist(datahist, bins=bin_width) 
    ax1.axvline(x=0, color='m', linewidth=3)
    
    ax1.set_xlim(left=range_[0], right=range_[1])
    ax1.set_ylabel('Count',fontsize=16)
    ax1.set_title('Peristimulus\nExpID {0}, Channel {1}, n = {2} trials'.format(experiment, current['channelID'], len(triggers)))

    ax2 = fig.add_subplot(212)
    for i in range(len(triggers) - 1):
        trial_raster = [(stamp - triggers[i])/fs for stamp in TimeStamps if stamp > triggers[i]+range_[0]*fs and stamp < triggers[i]+ range_[1]*fs]
        ax2.plot(trial_raster, np.transpose(i*np.ones([1,len(trial_raster)])),'|b')

    ax2.set_xlim(left=range_[0], right=range_[1])
    ax2.set_xlabel('Trial Window, s',fontsize=16)
    ax2.set_ylabel('Trial Number',fontsize=16)
    ax2.set_title('Raster\nChannel {0}, n = {1} trials'.format( current['channelID'], len(triggers) ))
    plt.show()
                    
    

                    

