# -*- coding: utf-8 -*-
"""
Example of how to extract and plot neural spike data saved in Blackrock nev data files
current version: 1.1.2 --- 08/04/2016

@author: Mitch Frankel - Blackrock Microsystems
"""

"""
Version History:
v1.0.0 - 07/05/2016 - initial release - requires brpylib v1.0.0 or higher
v1.1.0 - 07/12/2016 - addition of version checking for brpylib starting with v1.2.0
                      simplification of entire example for readability
                      plot loop now done based on unit extraction first
v1.1.1 - 07/22/2016 - minor modifications to use close() functionality of NevFile class
v1.1.2 - 08/04/2016 - minor modifications to allow use of Python 2.6+
"""


import matplotlib.pyplot as plt
import numpy             as np
from NEV.PY_blackrock.brpylib             import NevFile, brpylib_ver

# Version control
brpylib_ver_req = "1.3.1"
if brpylib_ver.split('.') < brpylib_ver_req.split('.'):
    raise Exception("requires brpylib " + brpylib_ver_req + " or higher, please use latest version")

# Init
chans    = np.arange(1,97)
datafile = './NEV/2AFC_stim_e20_trenes_20_ms_100_ancho_pulso_Frec_100_I_8_020.nev'

# Open file and extract headers
nev_file = NevFile(datafile)

# Extract data and separate out spike data
# Note, can be simplified: spikes = nev_file.getdata(chans)['spike_events'], shown this way for general getdata() call
nev_data = nev_file.getdata(list(chans))
spikes   = nev_data['spike_events']

# Close the nev file now that all data is out
nev_file.close()
#%%
spike_dict = {'ExperimentID':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[]}

spikes.keys()
spikes['Units']
len(spikes['ChannelID'])
len(spikes['TimeStamps'])
len(spikes['Waveforms'])

for it,channel in enumerate(spikes['ChannelID']):
    for timestamp, waveform in zip(spikes['TimeStamps'][it], spikes['Waveforms'][it]):
        spike_dict['ChannelID'].append(channel)
        spike_dict['TimeStamps'].append(timestamp)
        spike_dict['Waveforms'].append(waveform)
        

#%%
# Initialize plots
colors      = 'kbgrm'
line_styles = ['-', '--', ':', '-.']
f, axarr    = plt.subplots(len(chans))
samp_per_ms = nev_file.basic_header['SampleTimeResolution'] / 1000.0

for i in range(len(chans)):

    # Extract the channel index, then use that index to get unit ids, extended header index, and label index
    ch_idx      = spikes['ChannelID'].index(chans[i])
    units       = sorted(list(set(spikes['Classification'][ch_idx])))
    ext_hdr_idx = spikes['NEUEVWAV_HeaderIndices'][ch_idx]
    lbl_idx     = next(idx for (idx, d) in enumerate(nev_file.extended_headers)
                       if d['PacketID'] == 'NEUEVLBL' and d['ElectrodeID'] == chans[i])

    # loop through all spikes and plot based on unit classification
    # note: no classifications in sampleData, i.e., only unit='none' exists in the sample data
    ymin = 0; ymax = 0
    t = np.arange(nev_file.extended_headers[ext_hdr_idx]['SpikeWidthSamples']) / samp_per_ms

    for j in range(len(units)):
        unit_idxs   = [idx for idx, unit in enumerate(spikes['Classification'][ch_idx]) if unit == units[j]]
        unit_spikes = np.array(spikes['Waveforms'][ch_idx][unit_idxs]) / 1000

        if units[j] == 'none':
            color_idx = 0; ln_sty_idx = 0
        else:
            color_idx = (units[j] % len(colors)) + 1
            ln_sty_idx = units[j] // len(colors)

        for k in range(unit_spikes.shape[0]):
            axarr[i].plot(t, unit_spikes[k], (colors[color_idx] + line_styles[ln_sty_idx]))
            if min(unit_spikes[k]) < ymin: ymin = min(unit_spikes[k])
            if max(unit_spikes[k]) > ymax: ymax = max(unit_spikes[k])

    if lbl_idx: axarr[i].set_ylabel(nev_file.extended_headers[lbl_idx]['Label'] + ' ($\mu$V)')
    else:       axarr[i].set_ylabel('Channel ' + str(chans[i]) + ' ($\mu$V)')
    axarr[i].set_ylim((ymin * 1.05, ymax * 1.05))
    axarr[i].locator_params(axis='y', nbins=10)

axarr[-1].set_xlabel('Time (ms)')
plt.tight_layout()
plt.show()
