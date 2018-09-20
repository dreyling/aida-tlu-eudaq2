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

def analyse_sample(data):
    # general
    total_triggers = len(data['timestamp_begin']) # timestamps are uint64
    # sample duration: find out clock restart --> negative time difference 
    diff_times_raw = np.int64(data['timestamp_begin'][1:] - data['timestamp_begin'][:-1])
    clock_restart_index = np.where(diff_times_raw < 0.)[0]
    #print "int64 --> negative", diff_times_raw[clock_restart_index]
    # total length = start (1st) + len-1 (2nd-end) * clock cycle + end
    tlu_cycles = len(clock_restart_index) - 1
    sample_length = (
        (aida_tlu_max_timestamp - data['timestamp_begin'][0]) +
        tlu_cycles * (aida_tlu_max_timestamp + 1) +
        (data['timestamp_begin'][-1] + 1) ) / aida_tlu_time_factor
    trigger_rate = total_triggers / sample_length
    text = (
        'Total triggers: {:d}\n'
        'Run duration: {:.1f} s (incl. {:d} AIDA TLU clock cycles)\n'
        'Trigger rate (average): {:.1f} Hz'.format(
            total_triggers,
            sample_length,
            tlu_cycles,
            trigger_rate))
    # optional for seeing TLU clock cycle 
    #diff_times = np.abs(diff_times_raw)
    return total_triggers, sample_length, trigger_rate, text



if __name__ == "__main__":
    # AIDA TLU specifics
    aida_tlu_time_factor = 1e9 # for ns in s
    time_scaling_factor = 1# in s ##1e3 # for s in ms
    aida_tlu_min_timestamp = 0
    aida_tlu_max_timestamp = 4294967295 # 2^32 - 1, uint32

    # data
    arguments = docopt(__doc__, version='analyze trigger')
    file_name = arguments['--input']
    output_name = file_name[5:-4]
    data = np.load(file_name)
    
    ############################
    # general and timeline 
    total_triggers, sample_length, trigger_rate, timeline_text = analyse_sample(data)
    print total_triggers, sample_length, trigger_rate, timeline_text
    if arguments['--plot'] == '0':
        # timeline
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.subplots_adjust(left=0.15, right=0.98, top=0.7, bottom=0.15)
        plt.plot(data['timestamp_begin']/ aida_tlu_time_factor * time_scaling_factor, 
                data['ni_trigger'],
                'k')
        ax.set_xlabel('Timestamp in s')
        ax.set_ylabel('Trigger ID')
        ax.text(0.05, 1.4, timeline_text,
            transform=ax.transAxes, verticalalignment='top', horizontalalignment='left')
        fig.savefig('output/' + output_name + '_timeline.pdf')

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
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
        ax.hist(pivot, bins=48)
        ax.set_xlabel(r'pivot pixel [row]')
        ax.set_ylabel('counts')
        #ax.set_yscale('log')
        fig.savefig('output/' + output_name + '_pivot.pdf')

    ############################
    # trigger interval
    # difference: take unit32 for right time difference (if >clock cycle) --> all positive 
    diff_times = (np.uint32(data['timestamp_begin'][1:]) - np.uint32(data['timestamp_begin'][:-1]))
    print "trigger intervals from", np.min(diff_times), "to", np.max(diff_times)
    dt_hist_text =  "Mean of dt: {} s".format(np.mean(diff_times) / 1e9)
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_times/aida_tlu_time_factor)
        ax.set_xlabel(r'${\Delta t}$ in s')
        ax.set_ylabel('consecutive triggers')
        ax.set_yscale('log')
        ax.text(0.05, 0.9, dt_hist_text,
                transform=ax.transAxes, verticalalignment='top', horizontalalignment='left')
        fig.savefig('output/' + output_name + '_dt_hist.pdf')
        plt.show()

    ############################
    # time from first trigger until last trigger
    #print data['trigger']
    #print data['ni_trigger']
    ni_trigger_total = len(np.where(data['trigger']==data['ni_trigger'])[0])
    trigger      = np.where(data['trigger']==data['ni_trigger'])[0][:-1]
    next_trigger = np.where(data['trigger']==data['ni_trigger'])[0][1:]
    last_trigger = np.where(data['trigger']==data['ni_trigger'])[0][1:]-1 
    print "\n", ni_trigger_total + np.sum(next_trigger - trigger - 1)

    # cut on full
    diff_times = np.abs(data['timestamp_begin'][next_trigger] - data['timestamp_begin'][trigger])
    print len(diff_times)
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
        plt.hist(diff_times/aida_tlu_time_factor, bins=100)
        ax.set_xlabel(r'${\Delta t}$')
        ax.set_ylabel('consecutive triggers')
        #ax.set_xscale('log')
        ax.set_yscale('log')
        fig.savefig('output/' + output_name + '_ni-dt_trigger.pdf')

    # cut on mimosa times
    diff_times = np.abs(data['timestamp_begin'][next_trigger] - data['timestamp_begin'][trigger])
    diff_times = diff_times[diff_times < 1e6]
    print diff_times[:13]
    print len(diff_times)
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
        plt.hist(diff_times/aida_tlu_time_factor, bins=50)
        ax.set_xlabel(r'${\Delta t}$')
        ax.set_ylabel('consecutive triggers')
        #ax.set_xscale('log')
        ax.set_yscale('log')
        fig.savefig('output/' + output_name + '_ni-dt_trigger-zoom.pdf')

    # cut on next to last 
    print "\ntesting\n"
    print data['trigger'][:20]
    print data['ni_trigger'][:20]
    print trigger[:13]
    print last_trigger[:13]
    #print next_trigger[:13]
    print data['timestamp_begin'][:13]

    diff_times = np.abs(data['timestamp_begin'][last_trigger+1] - data['timestamp_begin'][trigger+1])
    print diff_times[:13]
    print len(diff_times)

    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
        plt.hist(diff_times/aida_tlu_time_factor, bins=50)
        ax.axvline(0.0001152)
        ax.axvline(0.0002304)
        ax.set_xlabel(r'${\Delta t}$')
        ax.set_ylabel('consecutive triggers')
        #ax.set_xscale('log')
        ax.set_yscale('log')
        fig.savefig('output/' + output_name + '_ni-dt_trigger-inner.pdf')
