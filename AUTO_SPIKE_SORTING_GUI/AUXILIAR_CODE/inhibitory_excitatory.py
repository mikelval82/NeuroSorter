# -*- coding: utf-8 -*- 
from decorators.time_consuming import timeit
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from xlsxwriter import Workbook

@timeit
def run(spike_dict, current):
    #------------ PARAMETERS TO BE SET BY USERS ----------------------------------------#########################
    experiment = 0    
    results_path = '/home/procesamiento/Escritorio/prueba.xlsx'      
    show = True                     
    #------------ DO NOT CHANGE ANYTHING ----------------------------------------#########################
    plt.close("all") 
    my_cmap = plt.get_cmap('Set1')
    fs = int(spike_dict['SamplingRate'][experiment])
    x_ticks = np.arange(0,48/fs,1/fs)*1000

    result = []
    for channel in np.unique(spike_dict['ChannelID']):
        print(channel)
        index = np.array([it for it,ch in enumerate(spike_dict['ChannelID']) if ch == channel and spike_dict['ExperimentID'][it] == experiment and spike_dict['UnitID'][it] != -1])
        waveforms = np.array(spike_dict['Waveforms'])[index]
        units = np.array(spike_dict['UnitID'])[index]

        for label in np.unique(units):
            unit = waveforms[units==label]
            mean_unit = unit.mean(axis=0)

            #% interpolation
            x = np.arange(0, 48)
            y = mean_unit
            f = interpolate.interp1d(x, y)
            xnew = np.arange(0, 47, 0.1)
            interpolated_unit = f(xnew)   # use interpolation function returned by `interp1d`

            #% find the key points
            x_min = np.argmin(interpolated_unit)
            amp_min = interpolated_unit[x_min]

            x_max = None
            for i in range(x_min,len(interpolated_unit)-5):
                gradient = np.diff(interpolated_unit[i:i+5])
                if  gradient.mean() > -1and gradient.mean() < 0:
                    x_max = i
                    break
            amp_max = interpolated_unit[x_max]
            
            if show:  
                plt.figure()
                plt.subplot(211)
                for it,wave in enumerate(unit):
                    plt.plot(x_ticks, wave, color=my_cmap(label))

                plt.subplot(212) 
                plt.plot(x_ticks, mean_unit, color= my_cmap(label))
                plt.plot((x_min*.1)/(fs/1000), interpolated_unit[x_min], '*', color='m')
                plt.plot((x_max*.1)/(fs/1000), interpolated_unit[x_max], '*', color='m')
                plt.suptitle('Channel->' + str(channel)+' unit->'+str(label))
                plt.show()

            result.append( {'channel':channel, 'unit':label, 'width':(x_max-x_min)*.1/(fs/1000), 'amplitude':(amp_max-amp_min)} )

    ordered_list=["channel","unit","width","amplitude"] #list object calls by index but dict object calls items randomly
    wb=Workbook(results_path)
    ws=wb.add_worksheet("New Sheet") #or leave it blank, default name is "Sheet 1"
    first_row=0
    for header in ordered_list:
        col=ordered_list.index(header) # we are keeping order.
        ws.write(first_row,col,header) # we have written first row which is the header of worksheet also.
     
    row=1
    for r in result:
        for _key,_value in r.items():
            col=ordered_list.index(_key)
            ws.write(row,col,_value)
        row+=1 #enter the next row
    wb.close()      