'''analyse trigger

Usage:
    analyse_mixed_mode.py (--input=<input>) [--plot=<plot>]

Options:
    --input=<input>             npy-file
    --plot=<plot>               Plot results [default: 0]
    -h --help                   show usage of this script
    -v --version                show the version of this script
'''

import numpy as np
import matplotlib.pyplot as plt
from docopt import docopt

if __name__ == "__main__":
    # data
    arguments = docopt(__doc__, version='analyze trigger')
    file_name = arguments['--input']
    output_name = file_name[5:-4]
    data = np.load(file_name)

    ############################
    # general

    # trigger rate
    triggers = len(data['run'])
    length = (data['timestamp_begin'][-1] - data['timestamp_begin'][0]) / 1e9
    trigger_rate = triggers / length
    timeline_text = ('Total triggers: {}\nRun duration: {} s\nTrigger rate (average): {} Hz'.format(triggers, length, trigger_rate))

    # trigger interval
    diff_times = np.abs(data['timestamp_begin'][1:] - data['timestamp_begin'][:-1])
    #diff_times = np.abs(data['timestamp_low'][1:] - data['timestamp_low'][:-1])


    # TODO: check th high numbers
    diff_times = diff_times[~diff_times > 18446744069415584]
    #print diff_times
    print "trigger intervals from", np.min(diff_times), "to", np.max(diff_times)

    dt_hist_text =  "Mean of dt: {} s".format(np.mean(diff_times) / 1e9)

    # Summary
    print timeline_text
    print dt_hist_text

    ############################
    # pivot pixel
    # with offset as in EUDAQ converter code
    rows = 576
    cycle_offset = 64
    cycles_per_row = 16 # 200ns 
    cycles_per_frame = cycles_per_row * rows # 9216
    pivot = ((cycles_per_frame + data['ni_pivot'] + cycle_offset) % cycles_per_frame) /16
    #pivot = data['ni_pivot']/16
    print "Pivot pixels from:", np.min(pivot), "to", np.max(pivot)
    fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
    ax.hist(pivot, bins=48)
    ax.set_xlabel(r'pivot pixel [row]')
    ax.set_ylabel('counts')
    #ax.set_yscale('log')
    #fig.savefig('output/' + output_name + '_pivot.pdf')

    ############################
    # time from first trigger until last trigger
    data['timestamp_begin']

    exit()
    



    # Plot
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(data['TimestampBegin']/1e6, data['TriggerN'])
        ax.set_xlabel('Timestamp in ms')
        ax.set_ylabel('Trigger ID')
        ax.text(0.05, 0.9, timeline_text,
                transform=ax.transAxes, verticalalignment='top', horizontalalignment='left')
        fig.savefig('output/' + output_name + '_timeline.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_times/1e6)
        ax.set_xlabel(r'${\Delta t}$ in ms')
        ax.set_ylabel('consecutive triggers')
        ax.set_yscale('log')
        ax.text(0.05, 0.9, dt_hist_text,
                transform=ax.transAxes, verticalalignment='top', horizontalalignment='left')
        fig.savefig('output/' + output_name + '_dt_hist.pdf')