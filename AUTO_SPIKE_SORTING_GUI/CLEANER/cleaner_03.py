# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
import matplotlib.pyplot as plt
import numpy as np

import umap
import networkx as nx
import community.community_louvain as community_louvain
import similaritymeasures

from scipy.stats import spearmanr
from scipy.stats import zscore
from scipy import signal

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
        
    def run(self, waveforms, n_neighbors=10, min_dist=.3, n_components=2, metric='manhattan'):
        self.__load_references()
        if len(waveforms) <= n_neighbors:
            unit_IDs = np.array([0]*len(waveforms))#self._filter_spikes(waveforms, np.zeros((len(waveforms),), dtype=int))#
        else:
            min_, max_ = waveforms.min(), waveforms.max()
            waveforms_norm = np.array([(wave - min_)/(max_ - min_) for wave in waveforms])
            reducer = umap.UMAP( n_neighbors=n_neighbors, min_dist=min_dist, 
                                n_components=n_components, metric=metric, 
                                set_op_mix_ratio=0.2 )
            reducer.fit_transform(waveforms_norm)
            embedding_graph = nx.Graph(reducer.graph_)
            partition = community_louvain.best_partition(embedding_graph)
            labels = [data[1] for data in list(partition.items())]
            
            unit_IDs = self._filter_spikes(waveforms_norm, labels)
        return unit_IDs

       
    def _filter_spikes(self, waveforms, labels):
        unit_IDs = np.zeros_like(labels)              
                
        for label in np.unique(labels):
            # -- select units from one cluster
            index = [i for i,x in enumerate(labels==label) if x]
            # ---  compute the mean of the cluster ----------------
            y = zscore(waveforms[index].mean(axis=0))

            spk_ccorr = 0
            for it, reference in enumerate(self.references):
                corr, _ = spearmanr(zscore(reference), y)
                if spk_ccorr < corr:
                    spk_ccorr = corr
                    final_reference = zscore(reference)
                    
            is_noise = False
            for it, antireference in enumerate(self.antireferences):
                corr, _ = spearmanr(zscore(antireference), y)
                if spk_ccorr < corr and corr > .95:
                    is_noise = True
                    final_antireference = zscore(antireference)
                    
            z = np.polyfit(np.arange(1,len(y)+1), y, 1)
            p = np.poly1d(z)
            
            final_reference_phase = np.vstack((final_reference[:-1], np.diff(final_reference)))
            y_phase = np.vstack((y[:-1], np.diff(y)))
                
            # -- check spike alignment --
            corr = signal.correlate(final_reference, y)
            desplazamiento = int(np.argmax(corr) - corr.size/2)
            print('desplazamiento ', abs(desplazamiento))
            if abs(desplazamiento) < 5:
                if desplazamiento < 0:
                    final_reference = final_reference[:desplazamiento]
                    y = y[abs(desplazamiento):]
                    final_reference_phase = np.vstack((final_reference[:-1], np.diff(final_reference)))
                    y_phase = np.vstack((y[:-1], np.diff(y)))
                elif desplazamiento > 0:
                    final_reference = final_reference[desplazamiento:]
                    y = y[:-desplazamiento]
                    final_reference_phase = np.vstack((final_reference[:-1], np.diff(final_reference)))
                    y_phase = np.vstack((y[:-1], np.diff(y)))
                        
            df = similaritymeasures.dtw(final_reference_phase, y_phase)[0]
            
            std = np.sum(np.std(zscore(waveforms[index], axis=1), axis=0))/48
            
            plt.figure()
            plt.subplot(211)
            plt.plot(y)
            plt.plot(np.arange(1,49)*p[1]+p[0], 'm')
            if is_noise:
                plt.plot(final_antireference, 'r')
            plt.plot(final_reference, 'g')
            plt.subplot(212)
#            
            
            if not is_noise and spk_ccorr > .7 and p[1]*100 > -2 and p[1]*100 < 3.5 and df < 6 and std < .6: #
                unit_IDs[index] = 1
                for wave in waveforms[index]:
                    plt.plot(zscore(wave), 'c')
            else:
                for wave in waveforms[index]:
                    plt.plot(zscore(wave), 'm')
            plt.suptitle('result ' + str(not is_noise and spk_ccorr > .7 and p[1]*100 > -2 and p[1]*100 < 3.5 and df < 6 and std < .6) + " isnoise " + str(is_noise) + "corr {:.2f}".format(spk_ccorr) + "p {:.2f}".format(p[1]*100) + "df {:.2f}".format(df)+"std {:.2f}".format(std))
            plt.show()
                            
        return unit_IDs
    
    


    
    
    
    
    
    
    
    
    
    
    
    
    