# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from DYNAMIC.dynamic import dynamic
from QTDesigner.sorter_mpl import Ui_MainWindows as  ui
from LOG.log import log
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QShortcut
from PyQt5.QtGui import QKeySequence
import numpy as np

class GUI_behaviour(QMainWindow, ui):

    def __init__(self, dmg):
        QMainWindow.__init__(self, parent=None)
        self.setupUi(self)
        self.show()
        
        self.dmg = dmg
        self.dyn = dynamic(self.dmg, self.listWidget_3, self.RawCode)
        self.dyn.load_auxiliar_code()
        self.log = log(self.logger)
        
        self.MplWidget.emitter.connect(self.manage_selection)
        
        self.btn_load.clicked.connect(self.openFileNameDialog)
        self.btn_save.clicked.connect(self.saveFileDialog)
        self.all_denoising_btn.clicked.connect(self.automatic_denoising)
        self.all_sorting_btn.clicked.connect(self.automatic_sorting)
        self.amplitude_threshold_btn.clicked.connect(lambda: self.update_amplitude_threshold())
        self.temporal_threshold_btn.clicked.connect(lambda: self.update_temporal_threshold())
        self.delete_btn.clicked.connect(lambda: self.delete())
        self.undo_btn.clicked.connect(lambda: self.undo())
        self.denoising_btn.clicked.connect(lambda: self.spikes_clean())
        self.sorting_btn.clicked.connect(lambda: self.sorting())
        self.all_in_btn.clicked.connect(lambda: self.all_in_one_step())
        self.btn_run.clicked.connect(lambda: self.dyn.load_module(self.listWidget_3.currentItem().text()))
        self.btn_save_changes.clicked.connect(self.dyn.save_script)
        
        self.channel_comboBox.activated.connect(lambda: self.toChannelID(self.channel_comboBox.currentText()))
        self.unit_comboBox.activated.connect(lambda: self.toUnitID(self.unit_comboBox.currentText()))
        self.U2ID_comboBox.activated.connect(lambda: self.selected_unit2ID(self.U2ID_comboBox.currentText()))
        
        self.global_shortcuts = self._define_global_shortcuts()
        self.update_U2ID_combobox()

    def _define_global_shortcuts(self):
        shortcuts = []
        sequence = {'Ctrl+Up':lambda: self.toChannelID('Up'), 
         'Ctrl+Down':lambda: self.toChannelID('Down'), 
         'Shift+Up':lambda: self.toUnitID('Up'), 
         'Shift+Down':lambda: self.toUnitID('Down'), 
         'Alt+0':lambda: self.selected_unit2ID('Noise'), 
         'Alt+1':lambda: self.selected_unit2ID(1), 
         'Alt+2':lambda: self.selected_unit2ID(2), 
         'Alt+3':lambda: self.selected_unit2ID(3), 
         'Alt+4':lambda: self.selected_unit2ID(4), 
         'Alt+5':lambda: self.selected_unit2ID(5), 
         'Alt+6':lambda: self.selected_unit2ID(6), 
         'Alt+7':lambda: self.selected_unit2ID(7), 
         'Alt+8':lambda: self.selected_unit2ID(8), 
         'Alt+9':lambda: self.selected_unit2ID(9), 
         'Ctrl+d':self.delete, 
         'Ctrl+z':self.undo, 
         'Ctrl+c':self.spikes_clean, 
         'Ctrl+s':self.sorting}
        for key, value in list(sequence.items()):
            s = QShortcut(QKeySequence(key), self, value)
            shortcuts.append(s)

        return shortcuts

    def toChannelID(self, action):
        self.log.myprint('ACTION == toChannelID->' + str(action))
        if action == 'Up':
            index = self.channel_comboBox.currentIndex()
            if index < self.channel_comboBox.count() - 1:
                self.channel_comboBox.setCurrentIndex(index + 1)
        elif action == 'Down':
            index = self.channel_comboBox.currentIndex()
            if index > 0:
                self.channel_comboBox.setCurrentIndex(index - 1)

        current_channel = int(self.channel_comboBox.currentText())
        self.dmg.current['channelID'] = current_channel
        self.update_unit_combobox(current_channel, 'All')
        units = self.dmg.show_unitID(self.unit_comboBox.currentText())
        self.update_view(units)

    def toUnitID(self, action):
        self.log.myprint('ACTION == toUnitID->' + str(action))
        if action == 'Up':
            index = self.unit_comboBox.currentIndex()
            if index < self.unit_comboBox.count() - 1:
                self.unit_comboBox.setCurrentIndex(index + 1)
        elif action == 'Down':
            index = self.unit_comboBox.currentIndex()
            if index > 0:
                self.unit_comboBox.setCurrentIndex(index - 1)
        elif action == 'None':
            self.unit_comboBox.setCurrentIndex(0)
        index = self.dmg.show_unitID(self.unit_comboBox.currentText())
        self.update_view(index)

    def selected_unit2ID(self, unit):
        if self.dmg.current['unitID'] == 'All':
            self.log.myprint_error('Unit ID modification is not allowed when current UnitID=All')
        else:
            self.log.myprint('ACTION == selected_unit2ID-> ' + str(unit))
            if unit == 'Noise':
                self.U2ID_comboBox.setCurrentIndex(0)
            else:
                self.U2ID_comboBox.setCurrentIndex(unit)
            index = self.dmg.selected_unit2ID(self.U2ID_comboBox.currentText())
            print('selected unit 2 id U2ID_comboBox, channel_comboBox, unit_comboBox', self.U2ID_comboBox.currentText(), self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
            self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
            self.update_view(index)

    def update_amplitude_threshold(self):
        self.log.myprint('UPDATE Amplitude Threshold range.')
        text = self.AmplitudeThreshold_Edit.text()
        r_min = int(text.split(',')[0].split('[')[1])
        r_max = int(text.split(',')[1].split(']')[0])
        index = self.dmg.clean_by_amplitude_threshold(r_min, r_max)
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)

    def update_temporal_threshold(self):
        self.log.myprint('UPDATE Temporal Threshold range.')
        text = self.TemporalThreshold_Edit.text()
        index = self.dmg.clean_by_temporal_threshold(window=(int(text)))
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)

    def delete(self):
        self.log.myprint('ACTION == Delete')
        index = self.dmg.delete()
        self.update_view(index)

    def undo(self):
        self.log.myprint('ACTION == Undo')
        index = self.dmg.undo()
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)

    def spikes_clean(self):
        self.log.myprint('ACTION == Spikes denoising in progress...')
        n_neighbors = int(self.n_neighbors_edit.text())
        min_dist = float(self.min_dist_edit.text())
        metric = self.metric_comboBox.currentText()
        
        index = self.dmg.clean(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
        self.log.myprint_out('ACTION == Spikes denoising is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)

    def sorting(self):
        if self.dmg.current['unitID'] == 'All':
            self.log.myprint_error('Sorting is not allowed when current UnitID=All')
        else:
            self.log.myprint('ACTION == Spikes sorting in progress...')
            n_neighbors = int(self.n_neighbors_edit.text())
            min_dist = float(self.min_dist_edit.text())
            metric = self.metric_comboBox.currentText()
            
            index = self.dmg.sort(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
            self.log.myprint_out('ACTION == Spikes sorting is done!')
            self.update_unit_combobox(self.channel_comboBox.currentText(), 'All')
            self.update_view(index)

    def all_in_one_step(self):
        self.log.myprint('ACTION == Spikes denoising in progress...')
        self.update_temporal_threshold()
        self.log.myprint_out('ACTION == Temporal threshold is done!')
        self.update_amplitude_threshold()
        self.log.myprint_out('ACTION == Amplitude threshold is done!')
        self.dmg.clean_all(n_neighbors=10, min_dist=0.1, metric='manhattan')
        self.log.myprint_out('ACTION == Spikes denoising is done!')
        index = self.dmg.sort_all(n_neighbors=20, min_dist=0.3, metric='manhattan')
        self.log.myprint_out('ACTION == Spikes sorting is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), 'All')
        self.update_view(index)

    def automatic_denoising(self):
        self.log.myprint('ACTION == Spikes denoising in progress...')
        n_neighbors = int(self.n_neighbors_edit.text())
        min_dist = float(self.min_dist_edit.text())
        metric = self.metric_comboBox.currentText()
        
        index = self.dmg.clean_all(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
        self.log.myprint_out('ACTION == Spikes denoising is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), 'All')
        self.update_view(index)

    def automatic_sorting(self):
        self.log.myprint('ACTION == Spikes sorting in progress...')
        n_neighbors = int(self.n_neighbors_edit.text())
        min_dist = float(self.min_dist_edit.text())
        metric = self.metric_comboBox.currentText()
        
        index = self.dmg.sort_all(n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
        self.log.myprint_out('ACTION == Spikes sorting is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), 'All')
        self.update_view(index)

    def update_view(self, index):
        self.log.myprint('channelID: ' + str(self.dmg.current['channelID']) + '-> unitID: ' + str(self.dmg.current['unitID']))
        self.manage_plotting(index)
        self.manage_average_plotting(self.dmg.current['channelID'])

    def manage_plotting(self, index):
        if index:
            waveforms = np.asarray(self.dmg.spike_dict['Waveforms'])[index]
            units = np.unique(np.asarray(self.dmg.spike_dict['UnitID'])[index])
            
            self.MplWidget.clear_plot()
            numUnits = []
            for unit in units:
                subindex = np.asarray(self.dmg.spike_dict['UnitID'])[index] == unit
                waveforms_unit = waveforms[subindex, :]
                numUnits.append(len(waveforms_unit))
                self.MplWidget.plot(waveforms_unit, unit)
            print('manage plotting units ', units, numUnits)
            self.MplWidget.plot_legend(units, numUnits)
        else:
            self.MplWidget.clear_plot()

    def manage_average_plotting(self, channelID):
        num = len(self.dmg.spike_dict['ChannelID'])
        index = [i for i in range(num) if self.dmg.spike_dict['ChannelID'][i] == channelID if self.dmg.spike_dict['UnitID'][i] != -1]
        if len(index) > 0:
            waveforms = np.asarray(self.dmg.spike_dict['Waveforms'])[index]
            units = np.unique(np.asarray(self.dmg.spike_dict['UnitID'])[index])
            self.MplWidget.clear_plot_units()
            for unit in units:
                subindex = np.asarray(self.dmg.spike_dict['UnitID'])[index] == unit
                self.MplWidget.plot_units(waveforms[subindex, :], unit)

        else:
            self.MplWidget.clear_plot_units()

    def manage_selection(self):
        x1 = self.MplWidget.regions['x1']
        y1 = self.MplWidget.regions['y1']
        x2 = self.MplWidget.regions['x2']
        y2 = self.MplWidget.regions['y2']
        x = np.arange(60)
        x_range = [i for i in range(60) if np.logical_and(x > x1, x < x2)[i]]
        if self.dmg.current['plotted']:
            plotted = np.asarray(self.dmg.current['plotted'])
            waveforms = np.asarray(self.dmg.spike_dict['Waveforms'])[plotted]
            self.manage_plotting(self.dmg.current['plotted'])
            self.dmg.current['selected'] = []
            for index in plotted:
                waveform = self.dmg.spike_dict['Waveforms'][index]
                if np.sum(np.logical_and(waveform[x_range] > y1, waveform[x_range] < y2)) > 0:
                    self.dmg.current['selected'].append(index)

            if self.dmg.current['selected']:
                selected = np.asarray(self.dmg.current['selected'])
                waveforms = np.asarray(self.dmg.spike_dict['Waveforms'])[selected]
                self.MplWidget.plot(waveforms, 0)

    def update_channel_combobox(self):
        channels = np.unique([channel for it, channel in enumerate(self.dmg.spike_dict['ChannelID']) if self.dmg.spike_dict['UnitID'][it] != -1])
        self.channel_comboBox.clear()
        [self.channel_comboBox.addItem(str(channel)) for channel in channels]

    def update_unit_combobox(self, channelID, unitID):
        channelID = int(channelID)
        units = np.unique([self.dmg.spike_dict['UnitID'][idx] for idx, channel in enumerate(self.dmg.spike_dict['ChannelID']) if channel == channelID if self.dmg.spike_dict['UnitID'][idx] != -1])

        self.unit_comboBox.clear()
        [self.unit_comboBox.addItem(str(unit)) for unit in units]
        self.unit_comboBox.addItem('All')
        self.unit_comboBox.addItem('Noise')

        AllItems = [self.unit_comboBox.itemText(i) for i in range(self.unit_comboBox.count())]
        
        if len(units) == 0:
            self.unit_comboBox.setCurrentIndex(1)
            self.dmg.current['unitID'] = 1
        else:
            
            if unitID != 'All' and unitID != 'Noise':
                self.unit_comboBox.setCurrentIndex(int(unitID)-1)
                self.dmg.current['unitID'] = int(unitID)
            elif unitID == 'All':
                index = [pos for pos,_ in enumerate(AllItems) if AllItems[pos] == 'All'][0]
                
                self.unit_comboBox.setCurrentIndex(index)
                self.dmg.current['unitID'] = unitID
            elif unitID == 'Noise':
                index = [pos for pos,_ in enumerate(AllItems) if AllItems[pos] == 'All'][0]

                self.unit_comboBox.setCurrentIndex(index)
                self.dmg.current['unitID'] = unitID

    def update_U2ID_combobox(self):       
        [self.U2ID_comboBox.addItem(str(unit)) for unit in ['Noise', 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        self.U2ID_comboBox.setCurrentIndex(0)

    def openFileNameDialog(self, btn):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileTypes = 'Nev Files (*.nev);;Mat Files (*.mat);;Python (*.npy)'
        fileNames, _ = QFileDialog.getOpenFileNames(self, 'QFileDialog.getOpenFileName()', '', fileTypes, options=options)
        for file in fileNames:
            self.log.myprint_in(file)

        try:
            self.dmg.load(fileNames)
            self.log.myprint_out('Loading completed.')
        except:
            self.log.myprint_error('Cannot load selected file.')

        self.update_channel_combobox()
        self.toChannelID('Down')
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, filetype = QFileDialog.getSaveFileName(self, 'QFileDialog.getSaveFileName()', '', '(*.npy)', options=options)
        self.dmg.save(fileName)
