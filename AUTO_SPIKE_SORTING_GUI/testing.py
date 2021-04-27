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
    full_spike_dict['FileNames'].append(file)
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

full_spike_dict = {'FileNames':[],'SamplingRate':[],'ExperimentID':[],'Active':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[],'Triggers':[],'Triggers_active':[]}
file = '2018_11_05_spontaneous001_UNITS_14_22_24_32_38_96.nev'

spike_dict = __nev_dict_neo(file, 0, full_spike_dict)

#%%
path = 'processed_'
def save_nev(path): 
    exp = 0
    for file in spike_dict['FileNames']:
        data = {'ChannelID':[], 'UnitID':[], 'TimeStamps':[], 'Waveforms':[], 'SamplingRate':None, 'Trigger':None}
        data['ChannelID'] = [val for it, val in enumerate(spike_dict['ChannelID']) if spike_dict['ExperimentID'][it] == exp and spike_dict['UnitID'][it] != -1]
        data['UnitID'] = [val for it, val in enumerate(spike_dict['UnitID']) if spike_dict['ExperimentID'][it] == exp and spike_dict['UnitID'][it] != -1]
        data['TimeStamps'] = [val for it, val in enumerate(spike_dict['TimeStamps']) if spike_dict['ExperimentID'][it] == exp and spike_dict['UnitID'][it] != -1]
        data['Waveforms'] = [val for it, val in enumerate(spike_dict['Waveforms']) if spike_dict['ExperimentID'][it] == exp and spike_dict['UnitID'][it] != -1]
        data['SamplingRate'] = spike_dict['SamplingRate'][exp]
        
        if path.split('/')[-1] != 'processed_':
            filename = path + '_' + str(exp) + '.nev'
        else:
            filename = path + file.split('/')[-1][:-4] + '.nev'
        try:
            binary = open(file, "rb")
            nev_file = open(filename, "wb")
            # write to file
            nev_file.write(binary.read(332))
            num_headers_binary = binary.read(4)
            nev_file.write(num_headers_binary)
            num_headers = unpack('<I',num_headers_binary)[0]
            nev_file.write(binary.read(num_headers*32))
            
            # save channels spike data
            for it, val in enumerate(data['ChannelID']):
                nev_file.write( pack('<I', data['TimeStamps'][it]) ) #timestamp
                nev_file.write( pack('<H', data['ChannelID'][it]) ) #packet_id
                nev_file.write( pack('<B', data['UnitID'][it]) ) #unit id
                nev_file.write( pack('<B', 0) ) # reserved
                for i in range(48): # waveform
                    nev_file.write( pack('h', data['Waveforms'][it][i]) )
            # save trigger data
            if len(spike_dict['Triggers'][exp]):
                data['Trigger'] = spike_dict['Triggers'][exp]
                print('paso')
                
                cont = 1
                for trigger in data['Trigger']:
                    triggerID = np.max(np.unique(data['ChannelID'])) + cont
                    cont+=1
                    for stamp in trigger:
                        nev_file.write( pack('<I', int(stamp)) ) #timestamp
                        nev_file.write( pack('<H', triggerID) ) #packet_id
                        nev_file.write( pack('<B', 0) ) #unit id
                        nev_file.write( pack('<B', 0) ) # reserved
                        for i in range(48): # waveform
                            nev_file.write( pack('h', 0) )
        except:
            print('Cannot save binary file: ')
        finally:
            binary.close()
            nev_file.close()
    
    
    


