# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
@DOI: 
"""
import numpy as np

def __python_dict(file):
    spike_dict = {'ExperimentID':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[]}
    append_channelID = spike_dict['ChannelID'].append
    append_TimeStamps = spike_dict['TimeStamps'].append
    append_Waveforms = spike_dict['Waveforms'].append
    append_UnitID = spike_dict['UnitID'].append
    append_OldID= spike_dict['OldID'].append
    append_ExperimentID = spike_dict['ExperimentID'].append
    
    aux = np.load(file, allow_pickle=True)
    dictionary = aux.item()
    
    [append_channelID(ChannelID) for ChannelID in dictionary['ChannelID']]
    [append_TimeStamps(TimeStamp) for TimeStamp in dictionary['TimeStamps']]
    [append_Waveforms(Waveform) for Waveform in dictionary['Waveforms']]
    [append_UnitID(UnitID) for UnitID in dictionary['UnitID']]
    [append_OldID(OldID) for OldID in dictionary['OldID']]
    [append_ExperimentID(ExperimentID) for ExperimentID in dictionary['ExperimentID']]
    
    return spike_dict

def temporal_threshold(spike_dict, window = 10, fs = 30000):
     
    index = np.array([it for it, unit in enumerate(spike_dict['UnitID']) if unit != -1])
    
    bin = int(fs*window/1000)
    max = np.array(spike_dict['TimeStamps'])[index].max()
    temporal_pattern = np.zeros( (96, int(max/bin)) )
    
    positions = []
    cols = []
    for it in index:
        stamp = spike_dict['TimeStamps'][it]
        ch = spike_dict['ChannelID'][it]
        position = int(stamp/bin)
        temporal_pattern[ch-1, position-1] = 1
        
        positions.append(it)
        cols.append(position)
       
    for col in range( temporal_pattern.shape[1] ):
        if np.sum( temporal_pattern[:,col] ) >= 10:
            iters = [it for it, x in zip(positions, cols) if x == col+1]
            for it in iters:
                spike_dict['UnitID'][it] = -1 
            
    return spike_dict
#%%

file = './prueba.npy'
spike_dict = __python_dict(file)

print(np.unique(spike_dict['ChannelID']))
#%%
from AUXILIAR_CODE import visualize_spikes_array as vsa


vsa.run(spike_dict, None)
      
spike_dict = temporal_threshold(spike_dict) 
                 
vsa.run(spike_dict, None)

#%%
import spikeinterface.extractors as se
import spikeinterface.toolkit as st
import spikeinterface.sorters as ss
import spikeinterface.comparison as sc
import spikeinterface.widgets as sw


recording, sorting_true = se.example_datasets.toy_example(duration=10, num_channels=4, seed=0)


w_ts = sw.plot_timeseries(recording, trange=[0,5])
w_rs = sw.plot_rasters(sorting_true, trange=[0,5])


channel_ids = recording.get_channel_ids()
fs = recording.get_sampling_frequency()
num_chan = recording.get_num_channels()

print('Channel ids:', channel_ids)
print('Sampling frequency:', fs)
print('Number of channels:', num_chan)


unit_ids = sorting_true.get_unit_ids()
spike_train = sorting_true.get_unit_spike_train(unit_id=unit_ids[0])

print('Unit ids:', unit_ids)
print('Spike train of first unit:', spike_train)

print('Available sorters', ss.available_sorters())
print('Installed sorters', ss.installed_sorters())


print(ss.get_default_params('mountainsort4'))
print(ss.get_default_params('klusta'))

recording_f = st.preprocessing.bandpass_filter(recording, freq_min=300, freq_max=6000)
recording_cmr = st.preprocessing.common_reference(recording_f, reference='median')

sorting_KL = ss.run_klusta(recording=recording_cmr)

print('Units found by Klusta:', sorting_KL.get_unit_ids())

snrs = st.validation.compute_snrs(sorting_KL, recording_cmr)
isi_violations = st.validation.compute_isi_violations(sorting_KL, duration_in_frames=recording_cmr.get_num_frames())
isolations = st.validation.compute_isolation_distances(sorting_KL, recording_cmr)

print('SNR', snrs)
print('ISI violation ratios', isi_violations)
print('Isolation distances', isolations)

sorting_curated_snr = st.curation.threshold_snrs(sorting_KL, recording_cmr, threshold=5, threshold_sign='less')
snrs_above = st.validation.compute_snrs(sorting_curated_snr, recording_cmr)

print('Curated SNR', snrs_above)


comp_gt_KL = sc.compare_sorter_to_ground_truth(gt_sorting=sorting_true, tested_sorting=sorting_KL)
comp_gt_KL.get_performance()
w_conf = sw.plot_confusion_matrix(comp_gt_KL)