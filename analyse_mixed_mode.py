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
        'Run duration: {:.1f} s (incl. {:d} full AIDA TLU clock cycles)\n'
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
    # for pivot from EUDAQ converter code
    rows = 576
    cycles_offset = 64
    cycles_per_row = 16 # 200ns 
    cycles_per_frame = cycles_per_row * rows # 9216

    # get and check data
    arguments = docopt(__doc__, version='analyze trigger')
    file_name = arguments['--input']
    output_name = file_name[5:-4]
    data = np.load(file_name)
    print "Check: NI Trigger ID bigger than TLU Trigger:", len(np.where(data['trigger'] < data['ni_trigger'])[0])
    #index = np.where(data['trigger'] < data['ni_trigger'])[0]
    #print index[:20]
    print ""

    ############################
    # general
    # Timeline 
    total_triggers, sample_length, trigger_rate, timeline_text = analyse_sample(data)
    if arguments['--plot'] == '2':
        # timeline
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.subplots_adjust(left=0.15, right=0.95, top=0.7, bottom=0.15)
        plt.plot(data['timestamp_begin']/ aida_tlu_time_factor * time_scaling_factor,
                data['ni_trigger'],
                'k')
        ax.set_xlabel('Time in s')
        ax.set_ylabel('Trigger ID')
        ax.text(0.05, 1.4, timeline_text,
            transform=ax.transAxes, verticalalignment='top', horizontalalignment='left')
        fig.savefig('output/' + output_name + '_timeline.pdf')

    # trigger interval distribution
    # difference: take unit32 for right time difference (if >clock cycle) --> all positive 
    diff_times = (np.uint32(data['timestamp_begin'][1:]) -
            np.uint32(data['timestamp_begin'][:-1]))
    #print "trigger intervals from", np.min(diff_times), "to", np.max(diff_times)
    if arguments['--plot'] == '2':
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        plt.hist(diff_times/aida_tlu_time_factor,
                bins=np.logspace(np.log10(0.000001),np.log10(1.0), 100),
                histtype='step', color='k',
                label='%d'%(len(diff_times)))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_xlabel(r'trigger interval ${\Delta t}$ in s')
        ax.set_ylabel('\# counts')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_trigger_intervals.pdf')

    # process data
    # MIMOSA, TODO: Understand why here +1 for the following
    print "trigger tlu (all)", data['trigger'][:15],    len(data['trigger'])
    print "trigger ni  (all)", data['ni_trigger'][:15], len(data['ni_trigger'])
    trigger_ni       = np.where(data['trigger']==data['ni_trigger'])[0][:-1]  +1
    next_trigger     = np.where(data['trigger']==data['ni_trigger'])[0][1:]   +1
    last_trigger     = np.where(data['trigger']==data['ni_trigger'])[0][1:]-1 +1
    print "trigger ni       ", trigger_ni[:15], len(trigger_ni)
    print "last trigger     ", last_trigger[:15], len(last_trigger)
    print "next trigger     ", next_trigger[:15], len(next_trigger)
    trigger_ni_index   = np.where(data['trigger']==data['ni_trigger'])[0][:-1]
    next_trigger_index = np.where(data['trigger']==data['ni_trigger'])[0][1:]
    last_trigger_index = np.where(data['trigger']==data['ni_trigger'])[0][1:]-1
    print "trigger ni index ", trigger_ni_index[:15], len(trigger_ni_index)
    total_ni_trigger = len(trigger_ni_index)
    print "Check:", total_ni_trigger + np.sum(next_trigger - trigger_ni - 1)
    print ""

    # Trigger multiplicity im Mimosa RO 
    trigger_in_mimosa = (last_trigger - trigger_ni) + 1
    print "trigger in mimosa", trigger_in_mimosa[:15], len(trigger_in_mimosa)
    print "trigger in mimosa (sum):", np.sum(trigger_in_mimosa)

    print "0 trigger (check)", len(np.where(trigger_in_mimosa == 0)[0])
    print "1 trigger ", len(np.where(trigger_in_mimosa == 1)[0])
    print "2 trigger ", len(np.where(trigger_in_mimosa == 2)[0])
    print "3 trigger ", len(np.where(trigger_in_mimosa == 3)[0])
    print "4 trigger ", len(np.where(trigger_in_mimosa == 4)[0])
    print "5 trigger ", len(np.where(trigger_in_mimosa == 5)[0])
    print "6 trigger ", len(np.where(trigger_in_mimosa == 6)[0])
    print "7 trigger ", len(np.where(trigger_in_mimosa == 7)[0])
    print "8 trigger ", len(np.where(trigger_in_mimosa == 8)[0])
    print "9 trigger ", len(np.where(trigger_in_mimosa == 9)[0])
    print "10 trigger", len(np.where(trigger_in_mimosa == 10)[0]), np.where(trigger_in_mimosa == 10)[0]
    if arguments['--plot'] == '2':
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        counts, bins, patches = ax.hist(trigger_in_mimosa,
                bins=np.linspace(1,11,11),
                histtype='step', color='k',
                label='%d entries'%(np.sum(np.histogram(trigger_in_mimosa)[0])))
        ax.set_xlabel(r'trigger in Mimosa RO')
        ax.set_ylabel('\# counts')
        #ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_multiplicity_mimosaRO.pdf')
        np.set_printoptions(suppress=True)
        print "bins : ", bins
        print "histo: ", counts, np.sum(counts)
        print "total: ", bins[:-1]*counts, np.sum(bins[:-1]*counts)
        print ""


    # intervals between ni trigger
    # --> busy time between 115.2 (min) to 230.4 us (max) 
    # --> folded with DESY II beam structure
    diff_times = np.abs(data['timestamp_begin'][next_trigger[:-1]] -
            data['timestamp_begin'][trigger_ni[:-1]])
    #diff_times = np.abs(data['timestamp_begin'][next_trigger_index] -
    #        data['timestamp_begin'][trigger_ni_index])
    print diff_times[:15], len(diff_times)
    if arguments['--plot'] == '2':
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        plt.hist(diff_times/aida_tlu_time_factor,
                bins=np.logspace(np.log10(0.000001),np.log10(1.0), 100),
                histtype='step', color='k',
                label='entries %d'%(len(diff_times)))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_ylabel('\# counts')
        ax.set_xlabel(r'NI trigger interval ${\Delta t}$ in s')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_ni_trigger_intervals.pdf')

    # intervals between first to last trigger in MimosaRO 
    # --> is always shorter than 230.4 us = 2x frames
    diff_times = np.abs(data['timestamp_begin'][last_trigger] -
            data['timestamp_begin'][trigger_ni])
    #diff_times = np.abs(data['timestamp_begin'][next_trigger_index] -
    #        data['timestamp_begin'][trigger_ni_index])
    mimosa_triggers_total = len(diff_times)
    print diff_times[:15], len(diff_times)
    # without 0 bin
    diff_times = diff_times[diff_times > 0.]
    mimosa_triggers_multiple = len(diff_times)
    mimosa_triggers_single = mimosa_triggers_total - mimosa_triggers_multiple
    if arguments['--plot'] == '2':
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        plt.hist(diff_times/aida_tlu_time_factor,
                bins=np.logspace(np.log10(0.000001),np.log10(0.001), 44),
                histtype='step', color='k',
                label='%d (2 to n triggers) = \n%d - %d (1 trigger evt.)'%(
                    mimosa_triggers_multiple,
                    mimosa_triggers_total,
                    mimosa_triggers_single))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_ylabel('\# counts')
        ax.set_xlabel(r'trigger intervals within one Mimosa-RO ${\Delta t}$ in s')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_maximum_trigger_intervals_in_NI-RO.pdf')

    # intervals in MimosaRO from 1st trigger
    # --> total trigger number minus NI trigger (if there are 2 triggers, only 1 interval)
    # plus 1
    diff_times = np.abs(data['timestamp_begin'][data['trigger'][:-1]] -
        data['timestamp_begin'][data['ni_trigger'][:-1]])
    # correctly as index would be like this
    #diff_times = np.abs(data['timestamp_begin'][data['trigger']-1] -
    #    data['timestamp_begin'][data['ni_trigger']-1])
    total_trigger = len(diff_times)
    print diff_times[:15], total_trigger
    # without 0 bin
    diff_times = diff_times[diff_times > 0.]
    multiple_trigger = len(diff_times)
    single_trigger = total_trigger - multiple_trigger
    print diff_times[:15], len(diff_times)
    frame_one = len(diff_times[diff_times < mimosa_frame*aida_tlu_time_factor])
    frame_two = len(diff_times[diff_times > mimosa_frame*aida_tlu_time_factor])
    print "time distance < 115.2us", frame_one
    print "time distance > 115.2us", frame_two
    if arguments['--plot'] == '2':
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        plt.hist(diff_times/aida_tlu_time_factor,
                bins=np.logspace(np.log10(0.000001),np.log10(0.001), 44),
                histtype='step', color='k',
                label='%d = %d ($<$115.2us) + \n %d ($>$115.2us) as 1st est.'%(
                    multiple_trigger,
                    frame_one,
                    frame_two))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_ylabel('\# counts')
        ax.set_xlabel('intervals (from 1st) within a Mimosa RO ${\Delta t}$ in s')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_all_trigger_intervals_in_NI-RO.pdf')
    print ""

    
    ############################
    # pivot pixel distribution
    pivot = ((cycles_per_frame + data['ni_pivot'][trigger_ni_index] + cycles_offset) % cycles_per_frame) / 16 # from EUDAQ converter
    total_pivot = len(pivot)
    print "Pivot pixels from:", np.min(pivot), "to", np.max(pivot)
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
        ax.hist(pivot, bins=72, histtype='step', color='k',
                label='%d'%(total_pivot))
        ax.set_xlabel(r'pivot pixel [row]')
        ax.set_ylabel('counts')
        ax.axvline(rows-1, color='k')
        #ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_pivot_pixel_distribution.pdf')


    # calculated busy time - maximum interval (first-last) in one NI-RO
    # start with 1
    diff_times = np.abs(data['timestamp_begin'][last_trigger] -
            data['timestamp_begin'][trigger_ni]) / aida_tlu_time_factor # in s
    possible_offset = 0
    busy_times = (rows-1-pivot+possible_offset)*200e-9 + mimosa_frame # in s
    print diff_times[:10], len(diff_times)
    print busy_times[:10], len(busy_times)
    # difference
    diff = busy_times[:] - diff_times[:]
    print diff[:10], len(diff)
    diff_wo0 = busy_times[diff_times > 0] - diff_times[diff_times > 0]
    print diff_wo0[:10], len(diff_wo0)
    print "Maximum trigger intervals in NI-RO:", len(diff_wo0)
    # TODO: understand this number? possible_offset = 7 no negative times 
    print "Negative times: #", len(diff[diff<0]), ", avg.", np.mean(diff[diff<0]), "std.", np.std(diff[diff<0])
    if arguments['--plot'] == '0':
        fig, ax = plt.subplots(figsize=(5, 4))#, dpi=100)
        ax.hist(diff_wo0,
                bins=np.logspace(np.log10(0.000001),np.log10(0.001), 44),
                histtype='step', color='k',
                label='%d'%(len(diff_wo0)))
        ax.axvline(mimosa_frame, color='k')
        ax.axvline(2*mimosa_frame, color='k')
        ax.set_xlabel(r'${\Delta t}=$ calc. busy time $-$ maximum interval in s')
        ax.set_ylabel('\# counts')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        fig.savefig('output/' + output_name + '_dt_calc_busy_time-max_interval.pdf')
    print ""

    # triggers within one frame: trigger interval has to be smaller then (rows-pivot)*200ns
    diff_times = np.abs(data['timestamp_begin'][data['trigger'][:-1]] -
        data['timestamp_begin'][data['ni_trigger'][:-1]])  / aida_tlu_time_factor
    # correctly as index would be like this
    #diff_times = np.abs(data['timestamp_begin'][data['trigger']-1] -
    #    data['timestamp_begin'][data['ni_trigger']-1])
    # without 0 bin
    total_trigger = len(diff_times)
    print diff_times[:15], total_trigger
    #diff_times = diff_times[diff_times > 0.]
    #total_trigger = len(diff_times)
    #print diff_times[:15], total_trigger

    pivot = ((cycles_per_frame + data['ni_pivot'] + cycles_offset) % cycles_per_frame) / 16 # from EUDAQ converter
    frame_duration = (rows-1-pivot[1:])*200e-9 # in s
    print frame_duration[:15], len(frame_duration)

    index = np.where(diff_times < frame_duration)[0]
    print len(index)
    index = np.where(diff_times[diff_times > 0.] < frame_duration[diff_times > 0.])[0]
    print len(index)

    print float(len(index)) / float(total_ni_trigger) * 100., "%"
