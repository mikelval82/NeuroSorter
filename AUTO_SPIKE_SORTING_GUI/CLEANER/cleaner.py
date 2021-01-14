# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from AUXILIAR_CODE.GLOBAL_CONSTANTS import SPIKES_RANGE, CLEANER_DEEPL_H5_MODEL, LOSS, OPTIMIZER, BATCH_SIZE
from keras.models import load_model
import numpy as np

class spike_denoiser:
    
    def __init__(self):
        self.__load_model()
    
    def __load_model(self):
        self.model = load_model(CLEANER_DEEPL_H5_MODEL, compile=False)
        self.model.compile(loss=LOSS, optimizer=OPTIMIZER, metrics=['accuracy'])
        print('model loaded')
        
    def run(self, waveforms, n_neighbors=None, min_dist=None, metric=None):
        print('run waveforms ', waveforms.shape)
        if waveforms.shape[1] == 60:
            waveforms = waveforms[:,SPIKES_RANGE] 
        elif waveforms.shape[1] == 48:
            waveforms = self.expand(waveforms)
        # minmax scaling in the range (0,1)
        for i in range(0,waveforms.shape[0]):
            waveforms[i,:] = (waveforms[i,:] - np.min(waveforms[i,:])) / (np.max(waveforms[i,:]) - np.min(waveforms[i,:])).astype(float)
            
        # inference on waveforms using the loaded model
        scores = self.model.predict_classes(waveforms, batch_size=BATCH_SIZE)
        print(scores)
        return np.logical_not(scores)
    
    def expand(self, waveforms):
        ini = np.zeros((6,))
        end = np.zeros((6,))
        w=[]
        for waveform in waveforms:
            waveform = waveform.squeeze()
            waveform = np.hstack((ini,waveform,end))
            w.append( waveform )
        waveforms = np.expand_dims(np.asarray(w), axis=-1)
    
        return waveforms

    
