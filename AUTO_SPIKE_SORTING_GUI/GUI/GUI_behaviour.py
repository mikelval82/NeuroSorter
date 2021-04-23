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
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QShortcut, QListWidgetItem
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import numpy as np

class GUI_behaviour(QMainWindow, ui):

    def __init__(self, dmg):
        QMainWindow.__init__(self, parent=None)
        self.setupUi(self)
        self.show()
        # init classes
        self.dmg = dmg
        self.log = log(self.logger)
        self.scripts_log = log(self.scripts_logger)
        self.dyn = dynamic(self.dmg, self.scripts_log, self.listWidget_3, self.RawCode)
        self.dyn.load_auxiliar_code()
        # callback emitter for waveforms selection in the spikes view
        self.MplWidget.emitter.connect(self.manage_selection)
        # Data Manager TAB
        self.btn_load.clicked.connect(self.openFileNameDialog)
        self.btn_save.clicked.connect(self.saveFileDialog)
        self.files_listWidget.clicked.connect(self.onClicked_file)
        self.channels_listWidget.clicked.connect(self.onClicked_channel)
        self.refresh_btn.clicked.connect(self.refresh_raster)
        self.radioButton.clicked.connect(self.active_channels)
        # Spikes view TAB
        self.all_denoising_btn.clicked.connect(self.automatic_denoising)
        self.all_sorting_btn.clicked.connect(self.automatic_sorting)
        self.amplitude_threshold_btn.clicked.connect(lambda: self.update_amplitude_threshold())
        self.temporal_threshold_btn.clicked.connect(lambda: self.update_cross_talk())
        self.delete_btn.clicked.connect(lambda: self.delete())
        self.undo_btn.clicked.connect(lambda: self.undo())
        self.denoising_btn.clicked.connect(lambda: self.spikes_clean())
        self.sorting_btn.clicked.connect(lambda: self.sorting())
        self.all_in_btn.clicked.connect(lambda: self.all_in_one_step())
        self.channel_comboBox.activated.connect(lambda: self.toChannelID(self.channel_comboBox.currentText()))
        self.unit_comboBox.activated.connect(lambda: self.toUnitID(self.unit_comboBox.currentText()))
        self.U2ID_comboBox.activated.connect(lambda: self.selected_unit2ID(self.U2ID_comboBox.currentText()))
        # Python scripts TAB
        self.btn_run.clicked.connect(lambda: self.dyn.load_module(self.listWidget_3.currentItem().text()))
        self.btn_save_changes.clicked.connect(self.dyn.save_script)
        self.btn_new_file.clicked.connect(self.create_file)
        # shortcuts management
        self.global_shortcuts = self._define_global_shortcuts()
        # initializations
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
            
        print(self.channel_comboBox.currentText())
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
                self.U2ID_comboBox.setCurrentIndex(int(unit))
            index = self.dmg.selected_unit2ID(self.U2ID_comboBox.currentText())
            self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
            self.update_view(index)

    def update_amplitude_threshold(self):
        self.log.myprint('UPDATE Amplitude Threshold range.')
        text = self.AmplitudeThreshold_Edit.text()
        r_min = int(text.split(',')[0].split('[')[1])
        r_max = int(text.split(',')[1].split(']')[0])
        [index, time_consumed] = self.dmg.clean_by_amplitude_threshold(r_min, r_max)
        self.log.myprint(time_consumed)
        self.log.myprint_out('ACTION == Amplitude Thresholding is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)

    def update_cross_talk(self):
        self.log.myprint('UPDATE Cross talk time interval.')
        text = self.TemporalThreshold_Edit.text()
        [index, time_consumed] = self.dmg.clean_by_cross_talk(window=(int(text)))
        self.log.myprint(time_consumed)
        self.log.myprint_out('ACTION == Cross talk analysis is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)
        
    def delete(self):
        self.log.myprint_out('ACTION == Delete')
        index = self.dmg.delete()
        self.update_view(index)

    def undo(self):
        self.log.myprint_out('ACTION == Undo')
        index = self.dmg.undo()
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)

    def spikes_clean(self):
        self.log.myprint('ACTION == Spikes denoising in progress...')
        [index, time_consumed] = self.dmg.clean(n_neighbors=15, min_dist=.1, metric='manhattan')
        self.log.myprint(time_consumed)
        self.log.myprint_out('ACTION == Spikes denoising is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        self.update_view(index)

    def sorting(self):
        if self.dmg.current['unitID'] == 'All':
            self.log.myprint_error('Sorting is not allowed when current UnitID=All')
        else:
            self.log.myprint('ACTION == Spikes sorting in progress...')
            [index, time_consumed] = self.dmg.sort(n_neighbors=15, min_dist=.1, metric='manhattan')
            self.log.myprint(time_consumed)
            self.log.myprint_out('ACTION == Spikes sorting is done!')
            self.update_unit_combobox(self.channel_comboBox.currentText(), 'All')
            self.update_view(index)
            
    def all_in_one_step(self):
        self.log.myprint('ACTION == Automatic analysis is in progress...')
        window = self.TemporalThreshold_Edit.text()
        threshold = self.AmplitudeThreshold_Edit.text()
        r_min = int(threshold.split(',')[0].split('[')[1])
        r_max = int(threshold.split(',')[1].split(']')[0])
        [index, time_consumed] = self.dmg.fully_automatic(window=(int(window)), r_min=r_min, r_max=r_max)
        self.log.myprint(time_consumed)
        self.log.myprint_out('ACTION == Automatic analysis is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), 'All')
        self.update_view(index)

    def automatic_denoising(self):
        self.log.myprint('ACTION == Spikes denoising in progress...')
        [index, time_consumed] = self.dmg.clean_all(n_neighbors=15, min_dist=.1, metric='manhattan')
        self.log.myprint(time_consumed)
        self.log.myprint_out('ACTION == Spikes denoising is done!')
        self.update_unit_combobox(self.channel_comboBox.currentText(), 'All')
        self.update_view(index)

    def automatic_sorting(self):
        self.log.myprint('ACTION == Spikes sorting in progress...')
        [index, time_consumed] = self.dmg.sort_all(n_neighbors=15, min_dist=0.1, metric='manhattan')
        self.log.myprint(time_consumed)
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
            sigmas = []
            for unit in units:
                subindex = np.asarray(self.dmg.spike_dict['UnitID'])[index] == unit
                waveforms_unit = waveforms[subindex, :]
                numUnits.append(len(waveforms_unit))
                
                max_ = waveforms_unit.mean(axis=0).max()
                min_ = waveforms_unit.mean(axis=0).min()
                mean_sigma = waveforms_unit.std(axis=0).mean()
                mean_sigma_norm = mean_sigma / abs(max_-min_)
                                
                sigmas.append( mean_sigma_norm )
                self.MplWidget.plot(waveforms_unit, unit)
            self.MplWidget.plot_legend(units, numUnits, sigmas)
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
        self.channel_comboBox.clear()        
        channels = self.dmg.spike_dict['ChannelID']
        activations = self.dmg.spike_dict['Active']
        channels_active = np.unique([channel for it,channel in enumerate(channels) if activations[it]])
        [self.channel_comboBox.addItem(str(channel)) for channel in channels_active]
                 
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
        
    def files_list(self):
        self.files_listWidget.clear()
        for file in self.dmg.spike_dict['FileNames']:
            item = QListWidgetItem( file.split('/')[-1][:-4] )
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            self.files_listWidget.addItem(item)
        
    def refresh_raster(self):
        self.raster_plot_frame.plot(self.files_listWidget.currentRow(), self.dmg.spike_dict)
        self.update_channel_combobox()
        self.toChannelID('Down')
        self.update_unit_combobox(self.channel_comboBox.currentText(), self.unit_comboBox.currentText())
        
    def active_channels(self):
        checked = self.radioButton.isChecked()
        if checked:
            item_state = Qt.Checked
        else:
            item_state = Qt.Unchecked
            
        self.dmg.active_channels(self.files_listWidget.currentRow(), checked)
        
        for index in range(self.channels_listWidget.count()):
            self.channels_listWidget.item(index).setCheckState(item_state)

    def onClicked_file(self, index):
        experimentID = index.row()
        channels, ch_activated = self.dmg.get_experiment_channels( experimentID )
        triggers, tr_active = self.dmg.get_experiment_triggers( experimentID )
        
        # -- add triggers
        self.channels_listWidget.clear()
        for it,timestamps in enumerate(triggers):
            item = QListWidgetItem( 'Trigger_' + str(it) + ': ' + str(len(timestamps)) + ' TimeStamps')
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if tr_active[it]:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.channels_listWidget.addItem(item)
        # -- add channels
        channels.sort()
        for it,channel in enumerate(channels):
            item = QListWidgetItem( str(channel) )
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if ch_activated[it]:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.channels_listWidget.addItem(item)

        self.refresh_raster()   
            
    def onClicked_channel(self, index):
        experimentID = self.files_listWidget.currentRow()
        channel = self.channels_listWidget.currentItem().text()

        if not self.channels_listWidget.item(index.row()).checkState():
            self.channels_listWidget.item(index.row()).setCheckState(Qt.Checked)
            if channel[:7] == 'Trigger':
                self.dmg.set_trigger_active(experimentID, index.row(), mode=True)
            else:
                self.dmg.set_channel_active(experimentID, int(channel), mode=True)
        else:
            self.channels_listWidget.item(index.row()).setCheckState(Qt.Unchecked)
            if channel[:7] == 'Trigger':
                self.dmg.set_trigger_active(experimentID, index.row(), mode=False)  
            else:
                self.dmg.set_channel_active(experimentID, int(channel), mode=False) 

    def openFileNameDialog(self, btn):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileTypes = 'Nev Files (*.nev);;Python (*.npy)'
        fileNames, _ = QFileDialog.getOpenFileNames(self, 'QFileDialog.getOpenFileName()', '', fileTypes, options=options)

        if fileNames:
            try:
                for file in fileNames:
                    self.log.myprint_in(file)
                
                [_,time_consumed] = self.dmg.load(fileNames)
                self.dmg.update_spike_dict('channels')
                self.files_list()
                self.log.myprint(time_consumed)
                self.log.myprint_out('Loading completed.') 
            except:
                self.log.myprint_error('Cannot load selected file.')

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileTypes = 'Nev Files (*.nev);;Python (*.npy)'
        fileName, filetype = QFileDialog.getSaveFileName(self, 'QFileDialog.getSaveFileName()', 'processed_', fileTypes, options=options)

        if filetype[:3] == 'Nev':  
            self.dmg.save_nev(fileName)
        elif filetype[:6] == 'Python':
            self.dmg.save_npy(fileName)
        
    def create_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, filetype = QFileDialog.getSaveFileName(self, 'QFileDialog.getSaveFileName()', '', '(*.py)', options=options)
        self.dyn.create(fileName + '.py')
