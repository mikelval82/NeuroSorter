# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from GUI.GUI_behaviour import GUI_behaviour 
from DATA_MANAGER.data_manager import data_manager
from CLEANER.cleaner import spike_denoiser
from SORTER.sorter_umap import sorter_umap as sorter
from PyQt5.QtWidgets import QApplication

import seaborn as sns
sns.set(style="darkgrid")
sns.set_context("notebook", rc={"lines.linewidth": 2.5})

import sys

class MyApp(QApplication):
    def __init__(self):
        QApplication.__init__(self,[''])
        #-------------------
        self.loadStyle() 
        ################# init GUI ################################
        self.spk = spike_denoiser()
        self.ae = sorter()
        self.dmg = data_manager(self.spk, self.ae)
        self.gui = GUI_behaviour(self.dmg)   
        
        sys.exit(self.exec_())

    def loadStyle(self):
        with open('QTDesigner/CSS/Fibrary.qss') as f:
            self.setStyleSheet(f.read())

if __name__ == "__main__":
    main = MyApp()
