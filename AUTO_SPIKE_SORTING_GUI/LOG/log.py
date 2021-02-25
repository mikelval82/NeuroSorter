# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from PyQt5 import QtGui, QtCore

class log():  
    
    def __init__(self,logger):
        self.logger = logger
        self.logger.setCenterOnScroll(True)
        
        self.tf = QtGui.QTextCharFormat()
        self.tf_green = QtGui.QTextCharFormat()
        self.tf_red = QtGui.QTextCharFormat()
        self.tf_yellow = QtGui.QTextCharFormat()
        self.tf_green.setForeground(QtGui.QBrush(QtCore.Qt.green))
        self.tf_red.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.tf_yellow.setForeground(QtGui.QBrush(QtCore.Qt.yellow))
        
    def myprint(self, text):
        self.logger.setCurrentCharFormat(self.tf)
        self.logger.appendPlainText(text)
        self.logger.centerCursor()
        self.logger.repaint()
    
    def myprint_in(self, text):
        self.logger.setCurrentCharFormat(self.tf_green)
        self.logger.appendPlainText("< "+text)
        self.logger.centerCursor()
        self.logger.repaint()
    
    def myprint_out(self, text):
        self.logger.setCurrentCharFormat(self.tf_yellow)
        self.logger.appendPlainText("> "+text)
        self.logger.centerCursor()
        self.logger.repaint()
        
    def myprint_error(self, text):
        self.logger.setCurrentCharFormat(self.tf_red)
        self.logger.appendPlainText(text)
        self.logger.centerCursor()
        self.logger.repaint()
        
    def clear(self):
        self.logger.clear()
    
   