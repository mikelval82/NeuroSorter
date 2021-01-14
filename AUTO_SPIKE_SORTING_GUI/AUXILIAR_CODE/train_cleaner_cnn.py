# -*- coding: utf-8 -*-
"""
@author: %(Mikel Val Calvo)s
@email: %(mikel1982mail@gmail.com)
@institution: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED))
"""


import matplotlib.pyplot as plt
import scipy.io as sio
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import *
from keras.utils import plot_model
from keras.models import model_from_json
from keras import regularizers
from keras import optimizers

from sklearn.manifold import TSNE
#from ggplot import *

#import pandas as pd
from sklearn.metrics import f1_score

#%%
######################## LOAD DATASET JAVIER ##############################################
#path = './CLEANER/javi_dataset/'
path = './CLEANER/javi_dataset/'

myfiles = ('spike_training_set1', 'Spike_test_dataset1')

data = sio.loadmat(path + myfiles[0] + '.mat')

train_data = data['training_set'].astype(float)
m = train_data.shape[0]
train_y = np.zeros((m,2))
train_y[0:int(m/2),0] = 1
train_y[int(m/2)+1:,1] = 1

data = sio.loadmat(path + myfiles[1] + '.mat')
test_data = np.transpose(data['test_dataset']).astype(float)
aux = np.transpose(data['test_clase'])
test_y = np.zeros((test_data.shape[0],2))
test_y[np.where(aux > 0),0] = 1
test_y[np.where(aux == 0),1] = 1

############# ****
data = np.vstack((train_data,test_data))
target = np.vstack((train_y,test_y))

#%% NORMALIZING
for i in range(0,data.shape[0]):
    data[i,:] = (data[i,:] - np.min(data[i,:])) / (np.max(data[i,:]) - np.min(data[i,:])).astype(float)
#index_noise = np.array([dataset['UnitID'][i] for i in range(len(dataset['UnitID'])) if (dataset['UnitID'][i] == -1)])
#index_spikes = np.array([dataset['UnitID'][i] for i in range(len(dataset['UnitID'])) if (dataset['UnitID'][i] > 0 )])
X_train, X_val, y_train, y_val = train_test_split(data, target, test_size=0.1, random_state=42)

############################ EXPANDIMOS LAS DIMENSIONES ###################################################

X_train = np.expand_dims(X_train,axis=-1).astype('float32')
X_val = np.expand_dims(X_val,axis=-1).astype('float32')

################################# MODELO ##############################################
from keras.layers import MaxPooling1D, BatchNormalization
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from tensorflow.keras.models import Sequential
###### NEW AIDRUIDS MODEL

model = Sequential()
model.add(Conv1D(16, 20, activation='relu', input_shape=(60, 1)))
model.add(BatchNormalization())

model.add(Conv1D(32, 10, activation='relu'))
pool = MaxPooling1D(2)
model.add(pool)
model.add(BatchNormalization())

model.add(Conv1D(64, 6, activation='relu'))
model.add(BatchNormalization())

model.add(Conv1D(128, 3, activation='relu'))
model.add(BatchNormalization())

model.add(Flatten())

model.add(Dropout(0.1))

model.add(Dense(2, activation='softmax'))
#

model.summary()
model.compile(loss='categorical_crossentropy',
              optimizer='Nadam',
              metrics=['accuracy'])
#
hist = model.fit(X_train, y_train, batch_size=32, epochs=20, validation_data=(X_val, y_val))

#%%
plt.plot(hist.history['acc'])
plt.plot(hist.history['val_acc'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

############################ SAVE MODEL #########################################33
# serialize model to JSON
model_json = model.to_json()
with open("./CLEANER/modelo_00.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("./CLEANER/modelo_00.h5")
print("Saved model to disk")

# WTF
model.save('./CLEANER/modelo_00.h5')