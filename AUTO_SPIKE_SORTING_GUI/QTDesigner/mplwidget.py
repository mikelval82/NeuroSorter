# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt

import numpy as np

class MplWidget(QWidget):
    emitter = QtCore.pyqtSignal()
    
    def __init__ (self, parent = None): 
        QWidget.__init__ (self, parent)
        #--
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.axes = self.figure.add_subplot(111)
        self.canvas.figure.patch.set_facecolor((0, 0, 0))
        self.canvas.axes.set_facecolor((0, 0, 0))
        self.canvas.axes.tick_params(axis='x', colors='white')
        self.canvas.axes.tick_params(axis='y', colors='white')
        self.canvas.axes.spines['bottom'].set_color('white')
        self.canvas.axes.spines['left'].set_color('white')

        self.axins = self.figure.add_axes([.7, .15, .2, .25]) 
        self.axins.tick_params(labelleft=False, labelbottom=False)
        #--
        vertical_layout = QVBoxLayout() 
        vertical_layout.addWidget(self.canvas)
        self.setLayout(vertical_layout)
        #--
        self.RS = RectangleSelector(self.canvas.axes, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1],  # don't use middle button
                                               minspanx=1, minspany=1,
                                               spancoords='pixels',
                                               interactive=True)
        #--
        self.regions = {'x1':None,'x2':None,'Y1':None,'y2':None}    
        #----------------------------------------------------------------------------------------
        self.my_cmap = plt.get_cmap('Set1')
 
    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        self.regions['x1'], self.regions['y1'] = eclick.xdata, eclick.ydata
        self.regions['x2'], self.regions['y2'] = erelease.xdata, erelease.ydata
        # -- callback to manage the selected region waveforms
        self.emitter.emit()
 
    def clear_plot(self):
        self.canvas.axes.clear()
        self.canvas.draw()
        
    def clear_plot_units(self):
        self.axins.clear()
        self.canvas.draw()
        
    def plot(self, data, unit=0):
        if len(data.shape) > 1:
            base = np.mgrid[:data.shape[0],:data.shape[1]][1]
            self.canvas.axes.plot(base.T,data.T, color=self.my_cmap(unit))
        else:
            self.canvas.axes.plot(np.arange(data.shape[1]),data, color=self.my_cmap(unit))  
        self.canvas.axes.set_ylabel('Voltaje ($\mu$V)', color='w', fontsize=20)
        self.canvas.axes.set_xlabel('Samples (n)', color='w', fontsize=20)
        self.canvas.draw()

    def plot_legend(self, units, numUnits):
        legends = []
        for index, unit in enumerate(units):
            legends.append(str(numUnits[index]) + ' Spikes of unit '+str(unit))
        leg = self.canvas.axes.legend(legends, loc='upper right')
        for index, unit in enumerate(units):
            leg.legendHandles[index].set_color(self.my_cmap(unit))
        self.canvas.draw()
        
    def plot_units(self, data, unit=0):
        mu = np.mean(data.T,axis=1)
        sigma = np.std(data.T,axis=1)
        self.axins.plot(mu, color=self.my_cmap(unit))
        self.axins.fill_between(np.arange(data.shape[1]), mu+sigma, mu-sigma, facecolor=self.my_cmap(unit), alpha=0.5)
        self.canvas.draw()

    def units_legend(self,units):
        units_str = ['Unit ' +str(i) for i in units]
        self.axins.legend(units_str, loc='upper center', bbox_to_anchor=(0.5, -.1), ncol=3, fancybox=True, shadow=True)
        self.canvas.draw()
        
