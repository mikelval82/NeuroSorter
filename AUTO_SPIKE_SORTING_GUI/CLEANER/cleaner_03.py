1957# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%

import numpy as np
from sklearn.preprocessing import StandardScaler
import umap

import networkx as nx
import community.community_louvain as community_louvain

from scipy.stats import spearmanr
import similaritymeasures
from scipy.stats import zscore

from os import listdir
from os.path import isfile, join

class spike_denoiser:
    
    def __init__(self):
        self.size_threshold = 1000
    
    def __load_references(self):
        mypath = './CLEANER/spike_templates/'
        self.references = []
        for file in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
            self.references.append( np.load(mypath + file) )
            
        mypath = './CLEANER/artefact_templates/'
        self.antireferences = []
        for file in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
            self.antireferences.append( np.load(mypath + file) )
            
        return True
        
    def run(self, waveforms, timestamps, sampling_rate, n_neighbors=10, min_dist=.3, n_components=2, metric='manhattan'):
        self.__load_references()
        if len(waveforms) <= n_neighbors:
            unit_IDs = np.array([0]*len(waveforms))#self._filter_spikes(waveforms, np.zeros((len(waveforms),), dtype=int))#
        else:
            waveforms_norm = np.array([(wave - waveforms.min())/(waveforms.max()-waveforms.min()) for it,wave in enumerate(waveforms)])
            reducer = umap.UMAP( n_neighbors=n_neighbors, min_dist=min_dist, 
                                n_components=n_components, metric=metric, 
                                set_op_mix_ratio=0.2 )
            reducer.fit_transform(waveforms_norm)
            embedding_graph = nx.Graph(reducer.graph_)
            partition = community_louvain.best_partition(embedding_graph)
            labels = [data[1] for data in list(partition.items())]
            
            unit_IDs = self._filter_spikes(waveforms_norm, timestamps, labels, sampling_rate)
        return unit_IDs

       
    def _filter_spikes(self, waveforms, timestamps, labels, sampling_rate):
        unit_IDs = np.zeros_like(labels)
        check = np.unique(labels)                
                
        for label in check:
            # -- select units from one cluster
            index = [i for i,x in enumerate(labels==label) if x]
            # ---  compute the features ----------------
            x = np.arange(1,49)
            y = waveforms[labels == label].mean(axis=0)
            
            which, ccorr = 0,0
            for it, reference in enumerate(self.references):
                corr, _ = spearmanr(reference, y)
                if ccorr < corr:
                    ccorr = corr
                    which = it
                    
            is_noise = False
            for it, antireference in enumerate(self.antireferences):
                corr, _ = spearmanr(antireference, y)
                if ccorr < corr:
                    is_noise = True
        
            reference = self.references[which]
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            df = similaritymeasures.frechet_dist(np.vstack((zscore(x),zscore(reference))), np.vstack((zscore(x),zscore(y))))
            yerr_zsc = StandardScaler().fit_transform(waveforms[labels == label].T).T.std(axis=0)
            std = np.sum(yerr_zsc) / waveforms.shape[1]
            # -- plot the figures ------------------------
            print('label ', label, ' isnoise ', is_noise, ' ccorr ', ccorr, ' p ', p, ' df ', df , ' std ', std)
            if label != -1 and not is_noise and ccorr > .7 and p[1]*100 > -100 and p[1]*100 < 150 and df < 5 and std < .5: 
                unit_IDs[index] = 1
                            
        return unit_IDs
    
    


    
    
    
    
    
    
    
    
    
    
    
    
    