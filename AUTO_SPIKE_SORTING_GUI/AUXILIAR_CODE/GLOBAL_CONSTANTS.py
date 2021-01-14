"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%

''' GRAPHICAL INTERFACE ASPECT ''' 
APP_CSS_STYLE = "QTDesigner/style_dark_orange.css"

'''Threshold in micro-volts for artifact rejection'''
THRESHOLD_RANGE = [-300,300]

''' THE DEEP LEARNING MODEL WHICH MAKES THE INFERENCE BETWEEN NOISE AND SPIKE EVENTS '''
CLEANER_DEEPL_H5_MODEL = "./CLEANER/model_0.h5"
LOSS='categorical_crossentropy'
OPTIMIZER='adam'
BATCH_SIZE = 16

'''RANGE OF THE EVENT TO BE ANALYZED'''
SPIKES_RANGE = range(15,50)
SPIKES_EXPAND = 6