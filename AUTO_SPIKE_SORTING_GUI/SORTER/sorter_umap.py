# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
import umap
import numpy as np
from sklearn import mixture
import similaritymeasures as sm

class sorter_umap:
    def __init__(self):
        pass
        
    def sort_spikes(self, spikes, n_neighbors=20, min_dist=.3, n_components=2, metric='manhattan'):       
        if spikes.shape[0] <= n_neighbors:
            unit_IDs = np.zeros((spikes.shape[0],), dtype=int) + 1
        else:
            # compute latent features
            reducer = umap.UMAP( n_neighbors=n_neighbors, min_dist=min_dist, n_components=n_components, metric=metric )
            embedding = reducer.fit_transform(spikes)
            # compute the optimal set of clusters
            unit_IDs = self._compute_BIC(embedding) + 1
            # revisite clusters
            if len(np.unique(unit_IDs)) > 1:
                mylist = self._detect_similarUnits(unit_IDs, spikes)
                unit_IDs = self._merge_similarClusters(mylist, unit_IDs, spikes)
            
        return unit_IDs

    def _compute_BIC(self, latent_features):
        lowest_bic = np.infty
        n_components_range = range(1, 7)
        
        for n_components in n_components_range:
            # Fit a Gaussian mixture with EM
            gmm = mixture.GaussianMixture(n_components=n_components,covariance_type='diag').fit(latent_features)

            bic_temp = gmm.bic(latent_features)
            if bic_temp < lowest_bic:
                lowest_bic = bic_temp
                best_gmm = gmm
    
        unit_IDs = best_gmm.predict(latent_features)
        return unit_IDs
    
    def _detect_similarUnits(self, units, spikes):
        means = []
        for label in np.unique(units):
            positions = [idx for idx,unit in enumerate(units) if unit == label]
            means.append( spikes[positions].mean(axis=0) )

        mylist = []
        my_index = list(range(len(means)))
        
        aux_means = means[1:]
        aux_myindex = my_index[1:]
        
        index = 0
        for _ in range(len(means)):
            main_mean = means[index]
            
            equal, distinct = [],[]
            for aux, idx in zip(aux_means,aux_myindex):
                print( 'distances ', sm.frechet_dist(main_mean, aux) )
                
                if sm.frechet_dist(main_mean, aux) < 10:
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
            
        
            
