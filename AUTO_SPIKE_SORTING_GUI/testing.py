#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 12:50:44 2021

@author: mikelval82
"""
from DATA_MANAGER.file_IO_01 import nev_manager 

class data_manager(nev_manager):
    
    def __init__(self):
        nev_manager.__init__(self)
  
    
    def initialize_spike_containers(self):
        self.current ={'channelID':None,'unitID':None,'plotted':[],'selected':[]}
        self.full_spike_dict = {'FileNames':[],'SamplingRate':[],'ExperimentID':[],'Active':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[],'Triggers':[],'Triggers_active':[]}
       
    def update_spike_dict(self, update):
        if update == 'triggers':
            self.spike_dict['Triggers_active'] = self.full_spike_dict['Triggers_active']
        elif update == 'channels':
            self.spike_dict = {'FileNames':[],'SamplingRate':[],'ExperimentID':[],'Active':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[],'Triggers':[],'Triggers_active':[]}
            self.spike_dict['FileNames'] = self.full_spike_dict['FileNames']
            self.spike_dict['SamplingRate'] = self.full_spike_dict['SamplingRate']
            self.spike_dict['Triggers'] = self.full_spike_dict['Triggers']
            self.spike_dict['Triggers_active'] = self.full_spike_dict['Triggers_active']
 
            for it,state in enumerate(self.full_spike_dict['Active']):
                if state:
                    self.spike_dict['ExperimentID'].append( self.full_spike_dict['ExperimentID'][it] )
                    self.spike_dict['Active'].append( self.full_spike_dict['Active'][it] )
                    self.spike_dict['ChannelID'].append( self.full_spike_dict['ChannelID'][it] )
                    self.spike_dict['UnitID'].append( self.full_spike_dict['UnitID'][it] )
                    self.spike_dict['OldID'].append( self.full_spike_dict['OldID'][it] )
                    self.spike_dict['TimeStamps'].append( self.full_spike_dict['TimeStamps'][it] )
                    self.spike_dict['Waveforms'].append( self.full_spike_dict['Waveforms'][it] )
        
#%% load data
file = ['2018_10_31_spontaneous_before_stimulation_sync_with_phosp002_sorteado_y_limpio_0.nev']
data = data_manager()
data.load(file)
spike_dict = data.spike_dict

#%% load templates
path = './CLEANER/spike_templates/'
templates = []


templates = np.array([np.load(path + 'spike_template_' + str(i) + '.npy') for i in range(115)])
    
print(len(templates))
#%% some statistics on templates
import matplotlib.pyplot as plt

plt.figure()
for wave in templates:
    plt.plot(wave)
#%% select a set ofwaveforms from one channel
import numpy as np
print(np.unique(spike_dict['ChannelID']))
spikes = np.array([wave for it,wave in enumerate(spike_dict['Waveforms']) if spike_dict['ChannelID'][it] == 32])
print(len(spikes))

    
#%%
import umap
import numpy as np
import networkx as nx
import community.community_louvain as community_louvain
import similaritymeasures as sm

n_neighbors=20
min_dist=.3
n_components=2
metric='manhattan'


# scaling
spikes_ = spikes[:,10:45]
min_, max_ = spikes_.min(), spikes_.max()
spikes_norm = np.array([(spk - min_)/(max_ - min_) for spk in spikes_])
# compute latent features
reducer = umap.UMAP( n_neighbors=min([n_neighbors,int(np.ceil(len(spikes_)/n_neighbors))]), min_dist=min_dist, n_components=n_components, metric=metric )
reducer.fit_transform(spikes_norm)
# compute the optimal set of clusters
embedding_graph = nx.Graph(reducer.graph_)
partition = community_louvain.best_partition(embedding_graph, resolution=1.1)
unit_IDs = np.array([data[1]+1 for data in list(partition.items())])
print(unit_IDs)
#%% compare with templates
plt.close('all')
for unit in np.unique(unit_IDs):
    unitgroup = spikes[unit_IDs == unit]
    unitgroup_mean = unitgroup.mean(axis=0)
    
    max_similarity = np.inf
    which = -1
    for it, template in enumerate(templates):
        template_phase = np.vstack((template[:-1], np.diff(template)))
        unitgroup_mean_phase = np.vstack((unitgroup_mean[:-1], np.diff(unitgroup_mean)))
        
        # -- check similarity ---
        similarity = sm.dtw(unitgroup_mean_phase, template_phase)[0]
        if max_similarity > similarity:
            max_similarity = similarity
            which = it
            
    print(max_similarity, which)
    plt.figure()
    plt.plot(unitgroup_mean)
    plt.plot(templates[which])
    
    unit_IDs[unit_IDs == unit] = which

print(np.unique(unit_IDs))

IDs = np.arange(len(np.unique(unit_IDs)))
final_unit_IDs = [IDs[list(np.unique(unit_IDs)).index(u)] for u in unit_IDs]

my_cmap = plt.get_cmap('Set1')

plt.figure()
for it,wave in enumerate(spikes):
    plt.plot(wave, color = my_cmap(final_unit_IDs[it]))

#%% revisite clusters
if len(np.unique(unit_IDs)) > 1:
    mylist = _detect_similarUnits(unit_IDs, spikes_norm, threshold=.7)
    unit_IDs = _merge_similarClusters(mylist, unit_IDs, spikes_norm)
            
       
  
def _detect_similarUnits(units, spikes, threshold=.8):
    means = []
    num_spikesXcluster = []
    for label in np.unique(units):
        positions = [idx for idx,unit in enumerate(units) if unit == label]
        num_spikesXcluster.append(len(positions))
        means.append( spikes[positions].mean(axis=0) )

    mylist = []
    my_index = list(range(len(means)))
    
    aux_means = means[1:]
    aux_myindex = my_index[1:]
    
    index = 0
    for it in range(len(means)):
        main_mean = means[index]

        equal, distinct = [],[]
        for aux, idx in zip(aux_means,aux_myindex):
            aux_phase = np.vstack((aux[:-1], np.diff(aux)))
            main_mean_phase = np.vstack((main_mean[:-1], np.diff(main_mean)))
            
            # -- check similarity ---
            similarity = sm.dtw(main_mean_phase, aux_phase)[0]
            print('-------------------------------------------------')
            print('umbral dinamico ', (1/np.mean(num_spikesXcluster[index]))+threshold)
            print('index ', index, ' num_spikesXcluster ', num_spikesXcluster)
            print('similarity ', similarity)
            
            if similarity < (1/np.mean(num_spikesXcluster))+threshold:
                equal.append(idx)
            else:
                distinct.append(idx)

        
        if equal:
            equal.append(index)
            mylist.append(equal)
        elif not equal and len(distinct) >= 1:
            mylist.append([my_index[index]])
        
        if not distinct:
            break
        elif len(distinct) == 1:
            mylist.append(distinct)
            break
        else:
            aux_means = [means[val] for val in distinct[1:]]
            aux_myindex = [my_index[val] for val in distinct[1:]]
            index = distinct[0]
            
    return mylist

def _merge_similarClusters(mylist, units, spikes):
    labels = np.unique(units)

    for idx, sublist in enumerate(mylist):
        for position in sublist:
            index = np.array([pos for pos,unit in enumerate(units) if unit == labels[position]])
            units[index] = (idx+1)*-1
    
    return abs(units)

    


