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
    max_ISIvalue=200
    ISI_bins = 30    

    index = current['plotted']
    time_stamps = np.empty((1,len(index)))
    for j in range(0,len(index)):
        time_stamps[0,j] = (spike_dict["TimeStamps"][index[j]])/20 #TimeStamp of each spike is obtained 
    time_stamps = time_stamps[0]    
    ISI = []
    for k in range(0,len(time_stamps)-1): #Goes through all spikes
        ISI.append(time_stamps[k+1]-time_stamps[k]) #Computed delay between two spikes
    ISI = np.array(ISI)
    
    plt.figure() 
    plt.hist(ISI[ISI<max_ISIvalue], bins = ISI_bins)
    plt.xlabel('Time (ms)')
    plt.ylabel('Spike count ' + str(len(np.squeeze(time_stamps))))
    plt.show()
        

        
    

        
        



