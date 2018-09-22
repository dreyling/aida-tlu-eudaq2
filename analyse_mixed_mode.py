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
    # Mimosa26 specifics
    mimosa_frame = 115.2e-6

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
        ax.hist(pivot, bins=72, histtype='step', color='k')
        ax.set_xlabel(r'pivot pixel [row]')
        ax.set_ylabel('counts')
        #ax.set_yscale('log')
        fig.savefig('output/' + output_name + '_pivot.pdf')

    ############################
    # trigger interval

    # total / for TLU
    # difference: take unit32 for right time difference (if >clock cycle) --> all positive 
    diff_times = (np.uint32(data['timestamp_begin'][1:]) - 
            np.uint32(data['timestamp_begin'][:-1]))
    print "trigger intervals from", np.min(diff_times), "to", np.max(diff_times)
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_times/aida_tlu_time_factor, 
                bins=np.logspace(np.log10(0.000001),np.log10(1.0), 100),
                histtype='step', color='k',
                label='%d'%(len(diff_times)))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_xlabel(r'${\Delta t}$ in s')
        ax.set_ylabel('\# trigger intervals')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_dt_hist.pdf')

    # MIMOSA, TODO: Understand why here +1 for the following
    trigger      = np.where(data['trigger']==data['ni_trigger'])[0][:-1]  +1
    next_trigger = np.where(data['trigger']==data['ni_trigger'])[0][1:]   +1
    last_trigger = np.where(data['trigger']==data['ni_trigger'])[0][1:]-1 +1
    print "NI trigger     ", trigger[:13]
    print "NI last_trigger", last_trigger[:13]
    print "NI next_trigger", next_trigger[:13]
    ni_trigger_total = len(np.where(data['trigger']==data['ni_trigger'])[0])
    print "\n", ni_trigger_total + np.sum(next_trigger - trigger - 1)

    # between Mimosa --> busy between 115.2 to 230.4 us folded with DESY II beam structure
    diff_times = np.abs(data['timestamp_begin'][next_trigger[:-1]] -
            data['timestamp_begin'][trigger[:-1]])
    print len(diff_times)
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_times/aida_tlu_time_factor,
                bins=np.logspace(np.log10(0.000001),np.log10(1.0), 100),
                histtype='step', color='k',
                label='entries %d'%(len(diff_times)))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_xlabel(r'${\Delta t}$ in s')
        ax.set_ylabel('\# intervals between Mimosa RO')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_ni-dt_trigger.pdf')

    # 1st to last trigger for Mimosa within in one RO frame --> is shorter than 2xframes 
    diff_times = np.abs(data['timestamp_begin'][last_trigger] -
            data['timestamp_begin'][trigger])
    mimosa_triggers_total = len(diff_times)
    # without 0 bin
    diff_times = diff_times[diff_times > 0.]
    mimosa_triggers_multiple = len(diff_times)
    mimosa_triggers_single = mimosa_triggers_total - mimosa_triggers_multiple

    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
        plt.hist(diff_times/aida_tlu_time_factor,
                bins=np.logspace(np.log10(0.000001),np.log10(0.001), 44),
                histtype='step', color='k',
                label='%d = %d (single) + %d (multiple)'%(
                    mimosa_triggers_total,
                    mimosa_triggers_single,
                    mimosa_triggers_multiple))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_xlabel(r'${\Delta t} in s$')
        ax.set_ylabel('\# intervals of first to last trigger within a Mimosa RO')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_ni-dt_trigger-inner.pdf')

    # All trigger intervals within in one Mimosa RO frame 
    print data['trigger'][:20]
    print data['ni_trigger'][:20]
    print data['trigger'][:20] - data['ni_trigger'][:20]
    #print "NI Trigger ID bigger than TLU Trigger after merge:", len(np.where(data['trigger'] - data['ni_trigger'] > 100)[0])
    #print "NI Trigger ID bigger than TLU Trigger after merge:", len(np.where(data['trigger'] < data['ni_trigger'])[0])

    print "NI Trigger 1", len(np.where(data['trigger'] - data['ni_trigger'] == 0)[0])
    print "NI Trigger 2", len(np.where(data['trigger'] - data['ni_trigger'] == 1)[0])
    print "NI Trigger 3", len(np.where(data['trigger'] - data['ni_trigger'] == 2)[0])
    print "NI Trigger 4", len(np.where(data['trigger'] - data['ni_trigger'] == 3)[0])
    print "NI Trigger 5", len(np.where(data['trigger'] - data['ni_trigger'] == 4)[0])
    print "NI Trigger 6", len(np.where(data['trigger'] - data['ni_trigger'] == 5)[0])
    print "NI Trigger 7", len(np.where(data['trigger'] - data['ni_trigger'] == 6)[0])
    print "NI Trigger 8", len(np.where(data['trigger'] - data['ni_trigger'] == 7)[0])
    print "NI Trigger 9", len(np.where(data['trigger'] - data['ni_trigger'] == 8)[0])
    print "NI Trigger 10", len(np.where(data['trigger'] - data['ni_trigger'] == 9)[0]), np.where(data['trigger'] - data['ni_trigger'] == 9)[0]
    print "NI Trigger 11", len(np.where(data['trigger'] - data['ni_trigger'] == 10)[0])
