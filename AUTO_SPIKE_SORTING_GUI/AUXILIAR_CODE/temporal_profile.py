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


    index = current['plotted']
    time_stamps = np.empty((1,len(index)))
    wave_forms = np.empty((48,len(index)))
    units = np.empty((1,len(index)))
    for j in range(0,len(index)):
        time_stamps[0,j] = (spike_dict["TimeStamps"][index[j]])/20 #TimeStamp of each spike is obtained 
        wave_forms[:,j] = (spike_dict["Waveforms"][index[j]]) #Waveform of each spike is obtained
        units[0,j] = spike_dict["UnitID"][index[j]]
        
    # Plotting
    colours = plt.get_cmap('Set1')    
    #Create a variable with the colours of interest
    plt.figure() #Create a figure
    plt.xlabel('Time (ms)')
    plt.ylabel('uV')
    for j in np.unique(units):
        trans = np.where(units==j) 
        #Select the spikes in each unit
        trans = trans[1]

        color = colours(int(j))
        for i in trans:
            k = np.round(time_stamps[0,i]) #Round the time stamps
            k = int(k)
            time_position = np.arange(k, k+48) #Give space to the spike
            
            plt.plot(time_position, wave_forms[:,i], color=color) 
        plt.show()
                
