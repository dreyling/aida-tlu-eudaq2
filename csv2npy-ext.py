'''convert csv data to npy-file

Usage:
    csv2npy.py (--input=<csv-file>)

Options:
    --input=<csv-file>          csv file
    -h --help                   show usage of this script
    -v --version                show the version of this script
'''

from docopt import docopt
import numpy as np

def csv2npy(filename):
    print "Loading csv file:", filename
    data = np.loadtxt(filename, delimiter=',', skiprows=1, dtype={
        'names': ('run', 'event', 'trigger', 'timestamp_low', 'timestamp_high', 'ni_trigger', 'ni_pivot'),
        'formats': ('uint32', 'uint32', 'uint32', 'uint64', 'uint64', 'uint32', 'uint32')})
    savename = filename[:-4] + '-ext.npy'
    print "Saving as npy file:", savename
    np.save(savename, data)
    print "Done!"


if __name__ == "__main__":
    arguments = docopt(__doc__, version='convert from csv to npy')
    filename = arguments['--input']

    csv2npy(filename)

    print "Test loading npy..."
    data = np.load(filename[:-4] + '-ext.npy')
    print "Names and types", data.dtype
    print "First entry:", data[0]
    print "Last entry:", data[-1]
    print "Total entries:", len(data['trigger'])
