# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%

import numpy as np
from sklearn.preprocessing import StandardScaler
import umap
from sklearn import mixture
from sklearn.neighbors import LocalOutlierFactor

from scipy.stats import spearmanr
import similaritymeasures
from scipy.stats import zscore

from os import listdir
from os.path import isfile, join

class spike_denoiser:
    
    def __init__(self):
        self.size_threshold = 1000
    
    def __load_references(self):
        mypath = './CLEANER/references/'
        self.references = []
        for file in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
            self.references.append( np.load(mypath + file) )
            
        mypath = './CLEANER/antireferences/'
        self.antireferences = []
        for file in [f for f in listdir(mypath) if isfile(join(mypath, f))]:
            self.antireferences.append( np.load(mypath + file) )
        
    def run(self, waveforms, n_neighbors=10, min_dist=.3, n_components=2, metric='manhattan'):
        self.__load_references()
        
        if waveforms.shape[0] <= n_neighbors:
            unit_IDs = self._filter_spikes(waveforms, np.zeros((waveforms.shape[0],), dtype=int))
        else:
            reducer = umap.UMAP( n_neighbors=n_neighbors, min_dist=min_dist, n_components=n_components, metric=metric, set_op_mix_ratio=0.2 )
            embedding = reducer.fit_transform(waveforms)
            labels = self._compute_BIC(embedding)
            outliers = self._filter_outliers(embedding)
            labels[outliers==-1] = -1
            unit_IDs = self._filter_spikes(waveforms, labels)
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
    
    def _filter_outliers(self, latent_features):
        return LocalOutlierFactor(contamination=0.2).fit_predict(latent_features)
       
    def _filter_spikes(self, waveforms, labels):
        unit_IDs = np.zeros_like(labels)
        check = np.unique(labels)
        
        for label in check:
            # ---  compute the features ----------------
            index = [i for i, x in enumerate(labels==label) if x]
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
            std = np.sum(yerr_zsc) / 48
            
            # -- plot the figures ------------------------
            if label != -1 and not is_noise and ccorr > .7 and p[1]*100 > -100 and p[1]*100 < 150 and df < 5 and std < .6: 
                unit_IDs[index] = 1
                            
        return unit_IDs

            
                
                    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    