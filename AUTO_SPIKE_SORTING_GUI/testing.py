#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 12:50:44 2021

@author: mikelval82
"""

#%%
from struct import unpack, pack

from neo import io
import numpy as np


def __nev_dict_neo(file, ExperimentID, full_spike_dict):
    # -- read the file
    reader = io.BlackrockIO(file)
    segment = reader.read_segment()
    # -- set sampling rate 
    full_spike_dict['SamplingRate'].append( segment.spiketrains[0].sampling_rate.magnitude )
    # -- set the triggers
    full_spike_dict['Triggers'].append([])
    full_spike_dict['Triggers_active'].append([])
    for it,event in enumerate(segment.events):
        if len(event.times) > 0:
            full_spike_dict['Triggers'][ExperimentID].append( event.times.magnitude * segment.spiketrains[0].sampling_rate.magnitude )
            full_spike_dict['Triggers_active'][ExperimentID].append(True)
    # -- preload functions
    append_channelID = full_spike_dict['ChannelID'].append
    append_TimeStamps = full_spike_dict['TimeStamps'].append
    append_Waveforms = full_spike_dict['Waveforms'].append
    append_UnitID = full_spike_dict['UnitID'].append
    append_OldID = full_spike_dict['OldID'].append
    append_ExperimentID = full_spike_dict['ExperimentID'].append
    append_active = full_spike_dict['Active'].append

    # -- assign data to spike_dict
    binary = open(file, "rb")
    binary.read(332)
    num_headers_binary = binary.read(4)
    num_headers = unpack('<I',num_headers_binary)[0]
    binary.read(num_headers*32)

    while True:
        try:
            timestamp = unpack('<I', binary.read(4))[0]
            packetid = unpack('<H', binary.read(2))[0]
            unit = unpack('<B', binary.read(1))[0]
            if unit == 0:
                unit = 1
            elif unit == 255:
                unit = -1
            unpack('<B', binary.read(1))#reserved 
            waveform = [unpack('h', binary.read(2))[0] for _ in range(48)]
                
            append_TimeStamps( timestamp )
            append_channelID( packetid )
            append_Waveforms( np.array(waveform) )
            append_UnitID(unit)
            append_OldID(None)
            append_ExperimentID(ExperimentID)
            append_active(True)
            
        except:
            break
 
    binary.close()   
    
    return full_spike_dict

#%%
from scipy import signal

full_spike_dict = {'FileNames':[],'SamplingRate':[],'ExperimentID':[],'Active':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[],'Triggers':[],'Triggers_active':[]}
file = './final_spontaneous_037_all_channels004.nev'

full_spike_dict = __nev_dict_neo(file, 0, full_spike_dict)
#%%
np.unique(full_spike_dict['ChannelID'])

unit = np.array([wave for it,wave in enumerate(full_spike_dict['Waveforms']) if full_spike_dict['ChannelID'][it] == 10])
print(unit.shape)
#%%
import matplotlib.pyplot as plt

plt.close('all')
plt.figure()
for data in unit:
    plt.plot(data)
#%%

reference = 12
# Print the obtained combinations
for it,wave in enumerate(unit):
    
    pos_min = np.argmin(wave[5:20])+5
    desplazamiento = reference-pos_min
    print(reference-pos_min)
    if desplazamiento < 0:
        unit[it] = np.hstack((wave[1:],np.zeros((abs(desplazamiento),))))
    elif desplazamiento > 0:
        unit[it] = np.hstack(( np.zeros((abs(desplazamiento),)), wave[:-abs(desplazamiento)], ))
    print(unit[it].shape)
    
    
    
    


