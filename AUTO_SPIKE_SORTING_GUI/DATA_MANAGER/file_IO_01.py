# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from decorators.time_consuming import timeit 

from neo import io
import numpy as np

class nev_manager:   
     
    @timeit
    def load(self, fileNames):
        self.initialize_spike_containers()
        
        self.ExperimentID = 0
        for file in fileNames:
            self.spike_dict['FileNames'].append(file.split('/')[-1])
            
            if file[-4:] == '.npy':
                self.__python_dict(file)
            elif file[-4:] == '.nev':
                self.__nev_dict(file, self.ExperimentID)
            self.ExperimentID += 1 
            
        return None
    
    def save(self, path): 
        exp = 0
        for file in self.spike_dict['FileNames']:
            data = {'ChannelID':[], 'UnitID':[], 'TimeStamps':[], 'Waveforms':[]}
            data['ChannelID'] = [val for it, val in enumerate(self.spike_dict['ChannelID']) if self.spike_dict['ExperimentID'][it] == exp]
            data['UnitID'] = [val for it, val in enumerate(self.spike_dict['UnitID']) if self.spike_dict['ExperimentID'][it] == exp]
            data['TimeStamps'] = [val for it, val in enumerate(self.spike_dict['TimeStamps']) if self.spike_dict['ExperimentID'][it] == exp]
            data['Waveforms'] = [val for it, val in enumerate(self.spike_dict['Waveforms']) if self.spike_dict['ExperimentID'][it] == exp]
            print(path, file)
            if path.split('/')[-1] != 'processed_':
                filename = path[:-10] + '_' + str(exp) + '.npy'
            else:
                filename = path + file[:-4] + '.npy'
            print(filename)
            np.save(filename, data)
            exp+=1
      
           
    def __nev_dict(self, file, ExperimentID):
        # -- read the file
        reader = io.BlackrockIO(file)
        segment = reader.read_segment()
        trigger = segment.events[0]
        # -- set the trigger
        self.spike_dict['SamplingRate'] = segment.spiketrains[0].sampling_rate.magnitude 
        self.spike_dict['Trigger'] = trigger.times.magnitude * segment.spiketrains[0].sampling_rate.magnitude
        # -- preload functions
        append_channelID = self.spike_dict['ChannelID'].append
        append_TimeStamps = self.spike_dict['TimeStamps'].append
        append_Waveforms = self.spike_dict['Waveforms'].append
        append_UnitID = self.spike_dict['UnitID'].append
        append_OldID= self.spike_dict['OldID'].append
        append_ExperimentID = self.spike_dict['ExperimentID'].append
        # -- assign data to spike_dict
        for channel in range(reader.unit_channels_count()):
            waveforms = reader.get_spike_raw_waveforms(unit_index=channel)
            timestamps = reader.get_spike_timestamps(unit_index=channel)
            for timestamp, waveform in zip(timestamps, waveforms):
                append_channelID(channel)
                append_TimeStamps(timestamp)
                append_Waveforms(waveform.squeeze())
                append_UnitID(1)
                append_OldID(None)
                append_ExperimentID(ExperimentID)
        
    def __python_dict(self, file):
        aux = np.load(file, allow_pickle=True)
        self.spike_dict = aux.item()


                
        

    
