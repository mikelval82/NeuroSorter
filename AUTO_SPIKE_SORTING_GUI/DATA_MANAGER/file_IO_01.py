# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from decorators.time_consuming import timeit 
from struct import unpack, pack

from neo import io
import numpy as np

class nev_manager:   
     
    @timeit
    def load(self, fileNames):
        self.initialize_spike_containers()
        
        self.ExperimentID = 0
        for file in fileNames:
            self.full_spike_dict['FileNames'].append(file)
            
            if file[-4:] == '.npy':
                self.__python_dict(file)
            elif file[-4:] == '.nev':
                self.__nev_dict_neo(file, self.ExperimentID)
     
            self.ExperimentID += 1 
            
        return None
    
    def __python_dict(self, file):
        aux = np.load(file, allow_pickle=True)
        self.full_spike_dict = aux.item()

    def __nev_dict_neo(self, file, ExperimentID):
        # -- read the file
        reader = io.BlackrockIO(file)
        segment = reader.read_segment()
        # -- set sampling rate 
        self.full_spike_dict['SamplingRate'].append( segment.spiketrains[0].sampling_rate.magnitude )
        # -- set the triggers
        self.full_spike_dict['Triggers'].append([])
        self.full_spike_dict['Triggers_active'].append([])
        for it,event in enumerate(segment.events):
            if len(event.times) > 0:
                self.full_spike_dict['Triggers'][ExperimentID].append( event.times.magnitude * segment.spiketrains[0].sampling_rate.magnitude )
                self.full_spike_dict['Triggers_active'][ExperimentID].append(True)
        # -- preload functions
        append_channelID = self.full_spike_dict['ChannelID'].append
        append_TimeStamps = self.full_spike_dict['TimeStamps'].append
        append_Waveforms = self.full_spike_dict['Waveforms'].append
        append_UnitID = self.full_spike_dict['UnitID'].append
        append_OldID = self.full_spike_dict['OldID'].append
        append_ExperimentID = self.full_spike_dict['ExperimentID'].append
        append_active = self.full_spike_dict['Active'].append

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
        
#                for channel in range(reader.unit_channels_count()):
#            ch = int( segment.spiketrains[channel].name.split('#')[0][2:] )
#            print(ch)
#            waveforms = reader.get_spike_raw_waveforms(unit_index=channel)
#            timestamps = reader.get_spike_timestamps(unit_index=channel)
#            print(waveforms, timestamps)
#            for timestamp, waveform in zip(timestamps, waveforms):
#                append_channelID(ch)
#                append_TimeStamps(timestamp)
#                append_Waveforms(waveform.squeeze())
#                append_UnitID(1)
#                append_OldID(None)
#                append_ExperimentID(ExperimentID)
#                append_active(True)
        
        
        
    def save_npy(self, path): 
        exp = 0
        for file in self.spike_dict['FileNames']:
            data = {'ChannelID':[], 'UnitID':[], 'TimeStamps':[], 'Waveforms':[], 'SamplingRate':None, 'Trigger':None}
            data['ChannelID'] = [channel for it, channel in enumerate(self.full_spike_dict['ChannelID']) if self.full_spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['UnitID'] = [unit for it, unit in enumerate(self.full_spike_dict['UnitID']) if self.full_spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['TimeStamps'] = [stamp for it, stamp in enumerate(self.full_spike_dict['TimeStamps']) if self.full_spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['Waveforms'] = [wave for it, wave in enumerate(self.full_spike_dict['Waveforms']) if self.full_spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['SamplingRate'] = self.full_spike_dict['SamplingRate'][exp]
            try:
                data['Trigger'] = self.full_spike_dict['Trigger'][exp]
            except:
                print('There is no Trigger to save!')

            if path.split('/')[-1] != 'processed_':
                filename = path + '_' + str(exp) + '.npy'
            else:
                filename = path + file.split('/')[-1][:-4] + '.npy'
            print(filename)
            np.save(filename, data)
            exp+=1
      
    def save_nev(self, path): 
        exp = 0
        for file in self.spike_dict['FileNames']:
            data = {'ChannelID':[], 'UnitID':[], 'TimeStamps':[], 'Waveforms':[], 'SamplingRate':None, 'Trigger':None}
            data['ChannelID'] = [val for it, val in enumerate(self.spike_dict['ChannelID']) if self.spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['UnitID'] = [val for it, val in enumerate(self.spike_dict['UnitID']) if self.spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['TimeStamps'] = [val for it, val in enumerate(self.spike_dict['TimeStamps']) if self.spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['Waveforms'] = [val for it, val in enumerate(self.spike_dict['Waveforms']) if self.spike_dict['ExperimentID'][it] == exp and self.spike_dict['UnitID'][it] != -1]
            data['SamplingRate'] = self.spike_dict['SamplingRate'][exp]
            
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
                if len(self.spike_dict['Triggers'][exp]):
                    data['Trigger'] = self.spike_dict['Triggers'][exp]
                    
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
                print('done')
    
            exp+=1
#        exp = 0
#        for file in self.spike_dict['FileNames']:
#            data = {'ChannelID':[], 'UnitID':[], 'TimeStamps':[], 'Waveforms':[], 'SamplingRate':None, 'Trigger':None}
#            data['ChannelID'] = [val for it, val in enumerate(self.spike_dict['ChannelID']) if self.spike_dict['ExperimentID'][it] == exp]
#            data['UnitID'] = [val for it, val in enumerate(self.spike_dict['UnitID']) if self.spike_dict['ExperimentID'][it] == exp]
#            data['TimeStamps'] = [val for it, val in enumerate(self.spike_dict['TimeStamps']) if self.spike_dict['ExperimentID'][it] == exp]
#            data['Waveforms'] = [val for it, val in enumerate(self.spike_dict['Waveforms']) if self.spike_dict['ExperimentID'][it] == exp]
#            data['SamplingRate'] = self.spike_dict['SamplingRate'][exp]
#            try:
#                data['Trigger'] = self.spike_dict['Trigger'][exp]
#            except:
#                data['Trigger'] = []
#                print('There is no Trigger to save!')
#            
#            if path.split('/')[-1] != 'processed_':
#                filename = path + '_' + str(exp) + '.nev'
#            else:
#                filename = path + file.split('/')[-1][:-4] + '.nev'
#            try:
#                binary = open(file, "rb")
#                nev_file = open(filename, "wb")
#                # write to file
#                nev_file.write(binary.read(332))
#                num_headers = binary.read(4)
#                nev_file.write(num_headers)
#                num_headers = unpack('<I',num_headers)[0]
#                nev_file.write(binary.read(num_headers*32))
#                for it, val in enumerate(data['ChannelID']):
#                    nev_file.write( pack('<I', data['TimeStamps'][it]) ) #timestamp
#                    nev_file.write( pack('<H', data['ChannelID'][it]) ) #packet_id
#                    if data['UnitID'][it] == -1:
#                        nev_file.write( pack('<B', 255) )                    
#                    else:
#                        nev_file.write( pack('<B', data['UnitID'][it]) ) #unit id
#                    
#                    nev_file.write( pack('<B', 0) ) # reserved
#                    
#                    for i in range(48): # waveform
#                        nev_file.write( pack('h', data['Waveforms'][it][i]) )
#                # save trigger data
#                if len(data['Trigger']):
#                    for stamp in data['Trigger']:
#                        nev_file.write( pack('<I', stamp) ) #timestamp
#                        nev_file.write( pack('<H', 131) ) #packet_id
#                        nev_file.write( pack('<B', 0) ) #unit id
#                        nev_file.write( pack('<B', 0) ) # reserved
#                        for i in range(48): # waveform
#                            nev_file.write( pack('h', np.zeros((48,),dtype='int32')[i]) )
#            except:
#                print('Cannot save binary file: ')
#            finally:
#                binary.close()
#                nev_file.close()
#
#            exp+=1

    
