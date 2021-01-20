# NeuroSorter Basics

Note: This document covers the basic information to use NeuroSorter Beta version

## 1 Dependencies

PyQt5, QtPy, h5py, umap-learn, seaborn, matplotlib, numpy, scikit-learn, scipy, similaritymeasures

All dependencies can be installed using:

git clone https://github.com/mikelval82/NeuroSorter-Interface.git

cd NeuroSorter-Interface

_pip install -r requirements.txt_

## 2 Overview

NeuroSorter is a spike cleaner and sorter. It works at three levels: First, it normalizes the data and discard abnormal shapes to remove noise events using a CNN; this network can be trained with previously cleaned data do adapt it to the specific recording of each setup. Then, putative units are sorted using a combination of an autoencoder to reduce dimensionality and clustering using Gaussian Mixture Models. This second step can be repeated to subsequently split desired units. At last, all units are visualized for manual curation; in addition, different functions are provided to facilitate the data curation (acor, data visualization, ISI).

## 3 NeuroSorter interface

![PySorter Scheme](https://github.com/[mikelval82]/[NeuroSorter-Interface]/blob/[main]/GUI_overview.png?raw=true)

## 4 Hotkeys
**Ctrl+Up/Down** -> move across channels.

**Shift+Up/Down** -> move across units on each channel.

**Alt+[0,1,2,3,4,5,6,7,8,9]** -> sends selected spikes to the specified unit, 0 unit is used for noise.

**Ctrl+c** -> clean spikes from noise for all the loaded waveforms.

**Ctrl+s** -> Sorting of current visualized waveforms.

**Ctrl+d** -> Send selected waveforms to noise, equivalent to Alt+0.

**Ctrl+z** -> Undo, only available for the last modification.




