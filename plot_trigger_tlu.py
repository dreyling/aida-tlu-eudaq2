'''analyse TLU

Usage:
    plot_trigger_tlu.py [--input=<input>]

Options:
    --input=<input>             filename npy 
    -h --help                   show usage of this script
    -v --version                show the version of this script
'''

import numpy as np
import matplotlib.pyplot as plt
from docopt import docopt



if __name__ == "__main__":
    # data
    ni_file = 'data/run_000044_ni.npy'
    ni = np.load(ni_file); print ni_file, "loaded"
    tlu_file = 'data/run_000044_tlu.npy'
    tlu = np.load(tlu_file); print tlu_file, "loaded"

    # analysis
    # general
    tlu_clock = 160e6 # Hz
    trigger_interval = 1600 # cycles or 1/tlu_clock
    trigger_rate = tlu_clock / trigger_interval
    print "Run 44: Autotrigger:", trigger_rate, "Hz"
    print "Total triggers:", len(tlu['TimestampBegin'])
    print "Run duration:", (tlu['TimestampBegin'][-1] - tlu['TimestampBegin'][0]) / 1e9, "s"


    # TLU
    tlu_duration = tlu['TimestampEnd'] - tlu['TimestampBegin']
    print "TLU trigger duration:", np.mean(tlu_duration), "ns"
    # cross checks
    #print len(tlu_duration[tlu_duration != 25])
    #print tlu['TimestampBegin'][0]
    #print tlu['TimestampBegin'][-1]
    #print np.min(tlu['TimestampBegin'])
    #print np.max(tlu['TimestampBegin'])

    if True:
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(tlu['TimestampBegin']/1000, tlu['TriggerN'])
        ax.set_xlabel('timestamp in us')
        ax.set_ylabel('Trigger ID')
        fig.savefig('output/run44_tlu_timeline.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(tlu['TimestampBegin'][:50000]/1000, tlu['TriggerN'][:50000])
        ax.set_xlabel('timestamp in us')
        ax.set_ylabel('Trigger ID')
        fig.savefig('output/run44_tlu_timeline_zoom.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(tlu['TimestampBegin'][:1000]/1000, tlu['TriggerN'][:1000])
        ax.set_xlabel('timestamp in us')
        ax.set_ylabel('Trigger ID')
        fig.savefig('output/run44_tlu_timeline_zoom_zoom.pdf')

    diff_tlu_times = tlu['TimestampBegin'][1:] - tlu['TimestampBegin'][:-1]
    print "Time difference of subsequent trigger", diff_tlu_times, "ns"
    print "Total mean:", np.mean(diff_tlu_times) / 1e9, "s"
    print len(diff_tlu_times[diff_tlu_times != 10000]), "entries having no 10us distance"
    print "Mean:", np.mean(diff_tlu_times[diff_tlu_times != 10000]) / 1e9, "s"
    #print np.min(diff_tlu_times[diff_tlu_times != 10000])
    print "effective Trigger rate:", (tlu['TriggerN'][-1] - tlu['TriggerN'][0]) / (
            (tlu['TimestampBegin'][-1] - tlu['TimestampBegin'][0]) / 1e9 ), "Hz"

    if True:
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_tlu_times/1000)
        ax.set_xlabel(r'${\Delta t}_{\rm TLU}$ in us')
        ax.set_ylabel('triggers')
        ax.set_yscale('log')
        fig.savefig('output/run44_tlu_dt_hist.pdf')

        #fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        #plt.hist(diff_tlu_times[diff_tlu_times != 10000]/1000)
        #ax.set_xlabel(r'${\Delta t}_{\rm TLU}$ in us')
        #ax.set_ylabel('triggers')
        #ax.set_yscale('log')
        #fig.savefig('output/run44_tlu_dt_hist_zoom_high.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_tlu_times[diff_tlu_times < 3500000]/1000)
        ax.set_xlabel(r'${\Delta t}_{\rm TLU}$ in us')
        ax.set_ylabel('triggers')
        ax.set_yscale('log')
        fig.savefig('output/run44_tlu_dt_hist_zoom_low.pdf')


    # Spectrum (FFT)
    if False:
        time_binning = 1e-9 # 1ns
        time_resolution = 1000 # = 1us

        # check times of triggers
        trigger_times = (tlu['TimestampBegin'] - tlu['TimestampBegin'][0]) / time_resolution # 1us
        print "Trigger times in us:", trigger_times
        print "Entries:", len(trigger_times)

        print "\n Look at a sample of 1s"
        length = 1e6 # us = 1s
        trigger_times_sample = trigger_times[trigger_times < length]
        print "Trigger times in the 1st second:", trigger_times_sample
        print "Entries:", len(trigger_times_sample)

        # x-time data: create array with length + 1 of highest trigger time
        # workaround to get ydata
        xdata = np.arange(trigger_times_sample[-1] + 1)
        print "Times in us:", xdata
        print "Entries:", len(xdata)

        # y-ampl (0/1) data:
        ydata = np.zeros(len(xdata))
        #print len(ydata); print ydata
        ydata[trigger_times_sample] = 1.
        print "Cross-check of triggers (1):", np.where(ydata != 0.)[0], "Entries:", len(ydata[ydata != 0.])

        # time spacing for fftfreq function`
        sample_spacing = time_resolution * time_binning
        print "Sample time: time spacing of sample (s):", sample_spacing
        scan_frequency = 1./sample_spacing
        print "Frequency (Hz):", scan_frequency

        # FFT
        ampl = np.fft.fft(ydata)
        print "FFT Amplitudes:", ampl

        # from: http://www.cbcity.de/die-fft-mit-python-einfach-erklaert
        N = len(ampl)/2 + 1
        print ampl[N-4:N+3]

        freqX = np.linspace(0, scan_frequency/2, N, endpoint=True)


        ## Freq function
        #freq = np.fft.fftfreq(len(xdata), sample_spacing)
        #print "FFT Frequencies:", freq
        #print np.max(freq)
        #print freq[freq < 0]

        # Plot
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        #plt.plot(freq, np.abs(ampl))
        #plt.plot(abs(ampl))
        plt.plot(freqX, np.abs(ampl[:N]))
        ax.set_xlabel(r'Frequency')
        ax.set_ylabel('Ampl.')
        ax.set_xscale('log')
        ax.set_yscale('log')
        fig.savefig('output/run44_tlu_spectrum.pdf')


    exit()

    ni_times = tlu['TimestampBegin'][ni['TriggerN'][ni['TriggerN'] <= tlu['TriggerN'][-1]] - 2]
    print ni_times, len(ni_times)

    if False:
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(ni_times, ni['TriggerN'][:len(ni_times)])
        ax.set_xlabel('timestamp in ns')
        ax.set_ylabel('Trigger ID')
        fig.savefig('output/run44_ni_timeline.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(ni_times[:50000], ni['TriggerN'][:len(ni_times)][:50000])
        ax.set_xlabel('timestamp in ns')
        ax.set_ylabel('Trigger ID')
        fig.savefig('output/run44_ni_timeline_zoom.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.plot(ni_times[:10000], ni['TriggerN'][:len(ni_times)][:10000])
        ax.set_xlabel('timestamp in ns')
        ax.set_ylabel('Trigger ID')
        fig.savefig('output/run44_ni_timeline_zoom_zoom.pdf')


    diff_ni_times = ni_times[1:] - ni_times [:-1]
    print diff_ni_times
    print diff_ni_times[diff_ni_times != 230000]

    if False:
        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_ni_times[diff_ni_times < 1e15])
        ax.set_xlabel(r'${\Delta t}_{\rm NI}$')
        ax.set_ylabel('triggers')
        ax.set_yscale('log')
        fig.savefig('output/run44_ni_dt_hist.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_ni_times[diff_ni_times != 230000])
        ax.set_yscale('log')
        fig.savefig('output/run44_ni_dt_hist_zoom_high.pdf')

        fig, ax = plt.subplots(figsize=(6, 4))#, dpi=100)
        plt.hist(diff_ni_times[diff_ni_times < 500000])
        ax.set_yscale('log')
        fig.savefig('output/run44_ni_dt_hist_zoom_low.pdf')


    exit()

    # plot
    fig, ax = plt.subplots(figsize=(8, 4))#, dpi=100)
    ydata_ni = np.ones(len(ni['TriggerN'])) + 1
    ydata_tlu = np.ones(len(tlu['TriggerN']))
    ax.plot(ni['TriggerN'], ydata_ni, ls='None', marker='o', label='NI')
    ax.plot(tlu['TriggerN'], ydata_tlu, ls='None', marker='o', label='TLU')
    ax.set_xlim(0, 65)
    ax.set_ylim(0.5, 3)
    ax.set_xlabel('Trigger ID')
    ax.set_ylabel('Device')
    ax.set_yticklabels([])
    ax.legend()
    fig.savefig('output/run44.pdf')

