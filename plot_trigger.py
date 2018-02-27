'''analyse trigger

Usage:
    plot_trigger.py (--input=<input>) [--plot=<plot>]

Options:
    --input=<input>             npy-file
    --plot=<plot>               Plot results [default: 0]
    -h --help                   show usage of this script
    -v --version                show the version of this script
'''

import numpy as np
import math
import matplotlib.pyplot as plt
from docopt import docopt

if __name__ == "__main__":
    # data
    arguments = docopt(__doc__, version='analyze trigger')
    file_name = arguments['--input']
    output_name = file_name[5:-4]
    data = np.load(file_name)

    # general
    triggers = len(data['timestamp_low'])
    length = (data['timestamp_low'][-1] - data['timestamp_low'][0]) / 1e9
    trigger_rate = triggers / length
    timeline_text = ('Total triggers: {}\nRun duration: {} s\nTrigger rate (average): {} Hz'.format(triggers, length, trigger_rate))

    diff_times = np.abs(data['timestamp_low'][1:] - data['timestamp_low'][:-1])

    diff_times = diff_times[~diff_times > 18446744069415584]
    print diff_times
    print np.max(diff_times)
    print np.min(diff_times)

    dt_hist_text =  "Mean of dt: {} s".format(np.mean(diff_times) / 1e9)
    #start_hist = math.log(diff_times[0])
    #end_hist = math.log(diff_times[-1])
    #print start_hist, end_hist

    print timeline_text
    print dt_hist_text

    # Plot
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(data['timestamp_low']/1e6, data['trigger_number'])
        ax.set_xlabel('Timestamp in ms')
        ax.set_ylabel('Trigger ID')
        ax.text(0.05, 0.9, timeline_text,
                transform=ax.transAxes, verticalalignment='top', horizontalalignment='left')
        fig.savefig('output/' + output_name + '_timeline.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_times/1e6
                , bins=np.logspace(-3, 2, 100))
        ax.set_xlabel(r'${\Delta t}$ in ms')
        ax.set_ylabel('consecutive triggers')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.text(0.05, 0.9, dt_hist_text,
                transform=ax.transAxes, verticalalignment='top', horizontalalignment='left')
        fig.savefig('output/' + output_name + '_dt_hist.pdf')
