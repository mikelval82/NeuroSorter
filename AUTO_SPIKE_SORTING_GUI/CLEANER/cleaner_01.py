# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from AUXILIAR_CODE.GLOBAL_CONSTANTS import SPIKES_RANGE

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, BatchNormalization, Activation, Dropout, MaxPooling2D
import numpy as np
import hdf5storage

class spike_denoiser:
    
    def __init__(self):
        self.__load_model()
    
    def __load_model(self):
        # Arrange them in a dictionary for direct initialization of the Keras model
        parameters_mat = hdf5storage.loadmat('./CLEANER/parameters.mat')
        parameters = {}
        parameters[f'input_mean'] = parameters_mat['input_mean']
        for i in range(1,7):
            parameters[f'conv{i}'] = [parameters_mat[f'conv{i}_weights'],
                                      parameters_mat[f'conv{i}_bias'].squeeze()]
            parameters[f'norm{i}'] = [parameters_mat[f'norm{i}_gamma'].squeeze(), 
                                      parameters_mat[f'norm{i}_beta'].squeeze(),
                                      parameters_mat[f'norm{i}_runningMean'].squeeze(),
                                      parameters_mat[f'norm{i}_runningVariance'].squeeze()]
        for i in range(1,3):
            parameters[f'fc{i}'] = [parameters_mat[f'fc{i}_weights'].T,
                                    parameters_mat[f'fc{i}_bias'].squeeze()]
        
        # Reproduce model architecture and initialize it with learnt parameters
        self.model_head = Sequential(name='head', layers=[
            Conv2D(25, (1, 3), weights=parameters['conv1'], name='conv_1', input_shape=(20, 50, 1)),
            BatchNormalization(epsilon=1e-5, weights=parameters['norm1'], name='batchnorm_1'),
            Activation('relu', name='relu_1'),
            Dropout(.5, name='dropout_1'),
            Conv2D(25, (20, 3), weights=parameters['conv2'], name='conv_2'),
            BatchNormalization(epsilon=1e-5, weights=parameters['norm2'], name='batchnorm_2'),
            Activation('relu', name='relu_2'),
            MaxPooling2D(pool_size=(1,2), strides=(1,1), name='maxpool_1'),
            Conv2D(50, (1, 3), weights=parameters['conv3'], name='conv_3'),
            BatchNormalization(epsilon=1e-5, weights=parameters['norm3'], name='batchnorm_3'),
            Activation('relu', name='relu_3'),
            Dropout(.5, name='dropout_2'),
            MaxPooling2D(pool_size=(1,2), strides=(1,1), name='maxpool_2'),
            Conv2D(100, (1, 3), weights=parameters['conv4'], name='conv_4'),
            BatchNormalization(epsilon=1e-5, weights=parameters['norm4'], name='batchnorm_4'),
            Activation('relu', name='relu_4'),
            MaxPooling2D(pool_size=(1,2), strides=(1,1), name='maxpool_3'),
            Conv2D(100, (1, 5), weights=parameters['conv5'], name='conv_5'),
            BatchNormalization(epsilon=1e-5, weights=parameters['norm5'], name='batchnorm_5'),
            Activation('relu', name='relu_5'),
            Dropout(.5, name='dropout_3'),
            MaxPooling2D(pool_size=(1,2), strides=(1,1), name='maxpool_4'),
            Conv2D(100, (1, 5), weights=parameters['conv6'], name='conv_6'),
            BatchNormalization(epsilon=1e-5, weights=parameters['norm6'], name='batchnorm_6'),
            Activation('relu', name='relu_6'),
            Dropout(.5, name='dropout_4'),
            MaxPooling2D(pool_size=(1,2), strides=(1,1), name='maxpool_5')])
            
        self.model_tail = Sequential(name='tail', layers=[
            Dense(100, weights=parameters['fc1'], name='fc_1', input_shape=(1, 2900)),
            Activation('relu', name='relu_7'),
            Dense(2, weights=parameters['fc2'], name='fc_2'),
            Activation('softmax', name='softmax')])
            
        self.parameters = parameters
        
    def __preprocessing(self, X, mean):
        X_norm = np.zeros_like(X, dtype='float')
        for i in range(X.shape[0]):
            X_norm[i,:,:,0] = (X[i,:,:,0] - mean)
        X_padded = np.pad(X_norm, pad_width=((0,0),(0,0),(1,1),(0,0)), mode='constant')
        return X_padded

    def run(self, waveforms):
        if waveforms.shape[1] == 60:
            waveforms = waveforms[:,SPIKES_RANGE]  
            
        num_batches = int(waveforms.shape[0]/20)
        resto = waveforms.shape[0]%20
        
        for i in range(20-resto):
            waveforms = np.vstack((waveforms.squeeze(), waveforms[-1].squeeze()))
        waveforms = np.expand_dims(waveforms, axis=-1)
        
        mydata = np.zeros((num_batches+1, 20,48,1))
        for i in range(num_batches+1):
            ini = i*20
            end = ini + 20
            mydata[i] = waveforms[ini:end]
        
        X_preprocessed = self.__preprocessing(mydata, mean=self.parameters['input_mean'])
        y_head = self.model_head.predict(X_preprocessed)
        # Flatten and reshape manually
        n_inputs = y_head.shape[0]
        X_FC = np.zeros((n_inputs, 1, 2900))
        for i in range(n_inputs):
            X_FC[i,0,:] = y_head[i].T.flatten()
        # Get model tail output, i.e. final prediction
        scores = self.model_tail.predict_classes(X_FC).flatten()
        scores_def = np.zeros((waveforms.shape[0]))
        for i in range(len(scores)):
            ini = i*20
            end = ini + 20
            scores_def[ini:end] = scores[i]
            
        scores_def = scores_def[:-(20-resto)]
            
        return scores_def
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    