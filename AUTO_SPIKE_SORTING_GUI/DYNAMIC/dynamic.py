# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
import sys 
import os

from os import listdir
from os.path import isfile, join
import importlib
from importlib import reload

class dynamic:
    
    
    def __init__(self, dmg, log, listWidget, RawCode):
        self.RawCode = RawCode
        self.listWidget = listWidget
        self.dmg = dmg
        self.log = log
        self.current_row = 0

    
    def load_module(self, fileName):
        ########### separo path y nombre del modulo ##############
        aux = fileName.split("/")
        path = ''
        for i in range(1, len(aux)-1):
            path += aux[i] + '/'
        module_name = aux[-1][:-3]
        #---------------------------------------------------------
        sys.path.append(os.path.realpath('./AUXILIAR_CODE/'))

        try:
            self.module = importlib.import_module(module_name)
            reload(self.module)
            [_,time_consumed] = self.module.run(self.dmg.spike_dict, self.dmg.current)
            self.log.myprint(time_consumed)
        except Exception as ex:
            self.log.myprint_error('Error -> ' + str(ex))
    
    def create(self, path):
        # Creates a new file 
        with open(path, 'w') as fp: 
             # To write data to new file  
             fp.write("# -*- coding: utf-8 -*- \nfrom decorators.time_consuming import timeit\n\n@timeit\ndef run(spike_dict, current):\n    pass") 
        # -- update listwidget scripts
        self.load_auxiliar_code()
        
    def save_script(self):
        script = self.listWidget.currentItem().text()
        code = self.RawCode.toPlainText()
        # open file in write mode
        f=open("./AUXILIAR_CODE/" + script, "w")
        f.write(code)
        f.flush()
        f.close()   
        # update values
        self.load_auxiliar_code()      
        self.edited = True
             
    def load_auxiliar_code(self):
        self.listWidget.clear()
        mypath = './AUXILIAR_CODE/'
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        for file in onlyfiles:
            self.listWidget.addItem(file)
            
        self.listWidget.itemClicked.connect(self.show_code)
        
        self.listWidget.setCurrentRow(self.current_row)
        self.show_code(self.listWidget.currentItem())
        
    def show_code(self, scriptItem):
        # read the file
        f=open("./AUXILIAR_CODE/" + scriptItem.text(), "r")
        contents =f.read()
        f.close()
        # update code viewer
        self.RawCode.setPlainText( contents )
        self.current_row = self.listWidget.currentRow() 
    
      
        
