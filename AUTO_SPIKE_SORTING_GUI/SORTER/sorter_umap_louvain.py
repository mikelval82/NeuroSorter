# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
import umap
import numpy as np
from scipy import signal

import networkx as nx
import community.community_louvain as community_louvain
import similaritymeasures as sm

class sorter:
    def __init__(self):
        pass
        
    def sort_spikes(self, spikes, n_neighbors=20, min_dist=.3, n_components=2, metric='manhattan'):       
        if spikes.shape[0] <= n_neighbors:
            unit_IDs = np.zeros((spikes.shape[0],), dtype=int) + 1
        else:
            # scaling
            spikes = spikes[:,10:45]
            spikes_norm = np.array([(wave - spikes.min())/(spikes.max()-spikes.min()) for it,wave in enumerate(spikes)])
            # compute latent features
            reducer = umap.UMAP( n_neighbors=min([n_neighbors,int(np.ceil(len(spikes)/n_neighbors))]), min_dist=min_dist, n_components=n_components, metric=metric )
            reducer.fit_transform(spikes_norm)
            # compute the optimal set of clusters
            embedding_graph = nx.Graph(reducer.graph_)
            partition = community_louvain.best_partition(embedding_graph, resolution=1.1)
            unit_IDs = np.array([data[1]+1 for data in list(partition.items())])
            # revisite clusters
            if len(np.unique(unit_IDs)) > 1:
                mylist = self._detect_similarUnits(unit_IDs, spikes_norm, threshold=1)
                unit_IDs = self._merge_similarClusters(mylist, unit_IDs, spikes_norm)
            
        return unit_IDs
  
    def _detect_similarUnits(self, units, spikes, threshold=1):
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
                # -- check spike alignment --
                corr = signal.correlate(aux, main_mean)
                desplazamiento = int(np.argmax(corr) - corr.size/2)
                print('desplazamiento ', desplazamiento)

                if abs(desplazamiento) < 5:
                    if desplazamiento < 0:
                        auxx = aux[:desplazamiento]
                        main_meanx = main_mean[abs(desplazamiento):]
                        aux_phase = np.vstack((auxx[:-1], np.diff(auxx)))
                        main_mean_phase = np.vstack((main_meanx[:-1], np.diff(main_meanx)))
                    elif desplazamiento > 0:
                        auxx = aux[desplazamiento:]
                        main_meanx = main_mean[:-desplazamiento]
                        aux_phase = np.vstack((auxx[:-1], np.diff(auxx)))
                        main_mean_phase = np.vstack((main_meanx[:-1], np.diff(main_meanx)))
                    
                # -- check similarity ---
                similarity = sm.dtw(main_mean_phase, aux_phase)[0]
                print( 'distances ', similarity )
                print('index ', index ,' dynamic threshold ', (1/np.mean(num_spikesXcluster))+threshold)
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

    def _merge_similarClusters(self, mylist, units, spikes):
        labels = np.unique(units)
    
        for idx, sublist in enumerate(mylist):
            for position in sublist:
                index = np.array([pos for pos,unit in enumerate(units) if unit == labels[position]])
                units[index] = (idx+1)*-1
        
        return abs(units)
            
        
            
