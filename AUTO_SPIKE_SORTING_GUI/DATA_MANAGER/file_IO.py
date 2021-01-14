# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from PY_blackrock.brpylib import NevFile, brpylib_ver
from scipy.signal import resample
import h5py
import numpy as np

from decorators.compute_time import compute_time

class nev_manager:   
     
    def load(self, fileNames):
        self.initialize_spike_containers()
        
        self.ExperimentID = 0
        for file in fileNames:
            if file[-4:] == '.npy':
                self.__python_dict(file)
            elif file[-4:] == '.mat':
                self.__mat_dict(file, self.ExperimentID)
            elif file[-4:] == '.nev':
                self.__nev_dict(file, self.ExperimentID)
            self.ExperimentID += 1   
    
    def save(self, path):
        np.save(path, self.spike_dict)
        
    def __mat_dict(self, file, ExperimentID):
        append_channelID = self.spike_dict['ChannelID'].append
        append_TimeStamps = self.spike_dict['TimeStamps'].append
        append_Waveforms = self.spike_dict['Waveforms'].append
        append_UnitID = self.spike_dict['UnitID'].append
        append_OldID= self.spike_dict['OldID'].append
        append_ExperimentID = self.spike_dict['ExperimentID'].append
        
        with h5py.File(file, 'r') as file:
            [append_channelID(channelID) for channelID in file['NEV']['Data']['Spikes'].get('Electrode')[:]]
            [append_TimeStamps(timestamp) for timestamp in file['NEV']['Data']['Spikes'].get('TimeStamp')[:]]
            [append_Waveforms( resample(waveform,48) ) for waveform in file['NEV']['Data']['Spikes'].get('Waveform')[:]]
            [append_UnitID(1) for timestamp in file['NEV']['Data']['Spikes'].get('TimeStamp')[:]]
            [append_OldID(None) for timestamp in file['NEV']['Data']['Spikes'].get('TimeStamp')[:]]
            [append_ExperimentID(ExperimentID) for timestamp in file['NEV']['Data']['Spikes'].get('TimeStamp')[:]]
           
    @compute_time
    def __nev_dict(self, file, ExperimentID):
        # Version control
        brpylib_ver_req = "1.3.1"
        if brpylib_ver.split('.') < brpylib_ver_req.split('.'):
            raise Exception("requires brpylib " + brpylib_ver_req + " or higher, please use latest version")

        nev_file = NevFile(file)
        spikes = nev_file.getdata(list(np.arange(1,97)))['spike_events']
        nev_file.close()
        
        append_channelID = self.spike_dict['ChannelID'].append
        append_TimeStamps = self.spike_dict['TimeStamps'].append
        append_Waveforms = self.spike_dict['Waveforms'].append
        append_UnitID = self.spike_dict['UnitID'].append
        append_OldID= self.spike_dict['OldID'].append
        append_ExperimentID = self.spike_dict['ExperimentID'].append
        
        for it,channel in enumerate(spikes['ChannelID']):
            for timestamp, waveform in zip(spikes['TimeStamps'][it], spikes['Waveforms'][it]):
                append_channelID(channel)
                append_TimeStamps(timestamp)
                append_Waveforms(resample(waveform,48)/1000)
                append_UnitID(1)
                append_OldID(None)
                append_ExperimentID(ExperimentID)
        
    def __python_dict(self, file):
        append_channelID = self.spike_dict['ChannelID'].append
        append_TimeStamps = self.spike_dict['TimeStamps'].append
        append_Waveforms = self.spike_dict['Waveforms'].append
        append_UnitID = self.spike_dict['UnitID'].append
        append_OldID= self.spike_dict['OldID'].append
        append_ExperimentID = self.spike_dict['ExperimentID'].append
        
        aux = np.load(file, allow_pickle=True)
        dictionary = aux.item()
        
        [append_channelID(ChannelID) for ChannelID in dictionary['ChannelID']]
        [append_TimeStamps(TimeStamp) for TimeStamp in dictionary['TimeStamps']]
        [append_Waveforms(resample(Waveform,48)) for Waveform in dictionary['Waveforms']]
        [append_UnitID(UnitID) for UnitID in dictionary['UnitID']]
        [append_OldID(OldID) for OldID in dictionary['OldID']]
        [append_ExperimentID(ExperimentID) for ExperimentID in dictionary['ExperimentID']]

                
        

    
