# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class RasterPlotWidget(QWidget):
    
    def __init__ (self, parent = None): 
        QWidget.__init__ (self, parent)
        #--
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.axes = self.figure.add_subplot(111)
        #add plot toolbar from matplotlib
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas.figure.patch.set_facecolor((0, 0, 0))
        self.canvas.axes.set_facecolor((0, 0, 0))
        self.canvas.axes.tick_params(axis='x', colors='white')
        self.canvas.axes.tick_params(axis='y', colors='white')
        self.canvas.axes.spines['bottom'].set_color('white')
        self.canvas.axes.spines['left'].set_color('white')
        self.canvas.axes.set_xlabel('Time[s]', color='white')
        self.canvas.axes.set_ylabel('Channels', color='white') 
        self.canvas.axes.grid(False)
        #--
        vertical_layout = QVBoxLayout() 
        vertical_layout.addWidget(self.toolbar)
        vertical_layout.addWidget(self.canvas)
        self.setLayout(vertical_layout)
        
        self.my_cmap = plt.get_cmap('Dark2')
        
    def plot(self, ExperimentID, spike_dict):
        self.canvas.axes.clear()
        
        fs = spike_dict['SamplingRate'][ExperimentID]
        
        channels = np.unique([ch for it,ch in enumerate(spike_dict['ChannelID']) if spike_dict['Active'][it] and spike_dict['ExperimentID'][it] == ExperimentID])

        for channel in channels:
            index_ch= [it for it, ch in enumerate(spike_dict['ChannelID']) if ch == channel and spike_dict['ExperimentID'][it] == ExperimentID and spike_dict['UnitID'][it] > 0]
            time_ch=np.array(spike_dict['TimeStamps'])[index_ch]/fs
        
            if len(time_ch>0):
                self.canvas.axes.plot(time_ch, np.transpose(channel*np.ones([1,len(time_ch)])),'|b')
                
        for it,trigger_list in enumerate( spike_dict['Triggers'][ExperimentID] ):
            if spike_dict['Triggers_active'][ExperimentID][it] == True:
                for timestamp in trigger_list:
                    self.canvas.axes.axvline(x=timestamp/fs, color=self.my_cmap(it))
                    
        self.canvas.axes.tick_params(axis='x', colors='white')
        self.canvas.axes.tick_params(axis='y', colors='white')
        self.canvas.axes.spines['bottom'].set_color('white')
        self.canvas.axes.spines['left'].set_color('white')
        self.canvas.axes.set_xlabel('Time[s]', color='white')
        self.canvas.axes.set_ylabel('Channels', color='white') 
        self.canvas.axes.grid(False)
        self.canvas.axes.set_title(spike_dict['FileNames'][ExperimentID].split('/')[-1][:-4], color='white') 
        self.canvas.draw()

