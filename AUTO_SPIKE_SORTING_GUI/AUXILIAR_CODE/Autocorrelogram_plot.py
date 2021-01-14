# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%

import numpy as np 
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import as_strided

def run(spike_dict,current):
    ''' 
        Dibujar el autocorrelograma de la unit en pantalla, la idea es más o menos la misma
        que en la figura anterior, coger todos los spikes del unit en pantalla, montar
        una serie temporal y calcularle el autocorrelograma
        También requiere acceso al spike_dict para ver cómo de largo es el registro
        Usa la función crosscorrelation definida abajo
    '''
    maxlag = 500
    autocorr_bin_size = 10

    index = current['plotted']

    time_stamps = np.empty((1,np.int(np.round(spike_dict["TimeStamps"][index[-1]]/20))))
    for j in range(0,len(index)-1):
        time_stamps[0,np.int(np.round(spike_dict["TimeStamps"][index[j]]/20))] =1 #TimeStamp of each spike is obtained 
 
    c = crosscorrelation(np.squeeze(time_stamps), np.squeeze(time_stamps), maxlag)

    c[maxlag] = 0   

    for l in range(len(c)-autocorr_bin_size):
        c[l] = np.sum(c[l:l+autocorr_bin_size-1])


    lags = np.arange(-maxlag,maxlag+1)
   
    plt.figure()
    plt.bar(lags, c, width = 1, color = 'k')
    plt.xlabel('Time (ms)')
    plt.ylabel('Corr coef')   
    plt.show()
    
def crosscorrelation(x, y, maxlag):	
    py = np.pad(y.conj(), 2*maxlag, mode='constant')
    T = as_strided(py[2*maxlag:], shape=(2*maxlag+1, len(y) + 2*maxlag),
                   strides=(-py.strides[0], py.strides[0]))
    px = np.pad(x, maxlag, mode='constant')
    return T.dot(px)
