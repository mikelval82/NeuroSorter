# NeuroSorter Basics

Note: This document covers the basic information to use NeuroSorter-Interface Beta version

## 1 Dependencies

python 3.7, PyQt5, QtPy, h5py, umap-learn, seaborn, matplotlib, numpy, scikit-learn, scipy, similaritymeasures

All dependencies can be installed using:

    git clone https://github.com/mikelval82/NeuroSorter-Interface.git

    cd NeuroSorter-Interface

    pip install -r requirements.txt
    
To run the GUI:
    
    cd AUTO_SPIKE_SORTING_GUI
    
    python3 AUTO_SPIKE_SORTING_GUI.py

## 2 Overview

NeuroSorter is a spike cleaner and sorter. ![Download Tutorial.mp4](https://github.com/mikelval82/NeuroSorter-Interface/blob/main/tutorial.mp4?raw=true)

## 3 NeuroSorter interface

![PySorter GUI Spikes-Viewer](https://github.com/mikelval82/NeuroSorter-Interface/blob/main/Images/GUI_overview.png?raw=true)

![PySorter GUI Scripts-Manager](https://github.com/mikelval82/NeuroSorter-Interface/blob/main/Images/code_panel.png?raw=true)

## 4 Hotkeys
**Ctrl+Up/Down** -> move across channels.

**Shift+Up/Down** -> move across units on each channel.

**Alt+[0,1,2,3,4,5,6,7,8,9]** -> sends selected spikes to the specified unit, 0 unit is used for noise.

**Ctrl+c** -> clean spikes from noise for all the loaded waveforms.

**Ctrl+s** -> Sorting of current visualized waveforms.

**Ctrl+d** -> Send selected waveforms to noise, equivalent to Alt+0.

**Ctrl+z** -> Undo, only available for the last modification.
