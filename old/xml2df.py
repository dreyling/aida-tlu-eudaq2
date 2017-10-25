'''convert xml data, produced with euCliReader from EUDAQ2, to npy-file

Usage:
    xml2df.py [--input=<filename> --max_event=<max_event>]

Options:
    --input=<input>             npy file [default: two_events.xml]
    --max_event=<max_event>     number [default: 2]
    -h --help                   show usage of this script
    -v --version                show the version of this script
'''

from docopt import docopt
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

def xml2df(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    data = pd.DataFrame(columns=['EventN', 'TriggerN', 'Timestamp'])
    for index, child in enumerate(root):
        #print index, child.tag, child.text
        event = {}
        trigger = {}
        timestamp = {}
        for subindex, subchild in enumerate(child):
            #print subindex, subchild.tag, subchild.text
            for subsubindex, subsubchild in enumerate(subchild):
                #print subsubindex, subsubchild.tag, subsubchild.text
                for subsubsubindex, subsubsubchild in enumerate(subsubchild):
                    #print subsubsubindex, subsubsubchild.tag, subsubsubchild.text
                    if subsubsubchild.tag == 'EventN':
                        #print subsubsubchild.tag, subsubsubchild.text
                        event = {subsubsubchild.tag : subsubsubchild.text}
                        #print event
                    if subsubsubchild.tag == 'TriggerN':
                        #print subsubsubchild.tag, subsubsubchild.text
                        trigger = {subsubsubchild.tag : subsubsubchild.text}
                        #print trigger
                    if subsubsubchild.tag == 'Timestamp' and subsubsubindex == 9:
                        #print subsubsubindex, subsubsubchild.tag, subsubsubchild.text.split('  ->  ')
                        timestamp = {subsubsubchild.tag : subsubsubchild.text.split('  ->  ')}
                        #print timestamp
        event.update(trigger)
        event.update(timestamp)
        data = data.append(event, ignore_index=True)
    return data

def xml2dfv2(filename, max_event):
    tree = ET.parse(filename)
    print "... parsing done"
    root = tree.getroot()
    print "... getroot done"
    data = pd.DataFrame(columns=['EventN', 'TriggerN', 'Timestamp'])
    for index, child in enumerate(root):
        #print index, child.tag, child.text
        event = {}
        trigger = {}
        timestamp = {}
        #print child[11][1].tag
        for subindex, subchild in enumerate(child[11][1]):
            #print subindex, subchild.tag, subchild.text
            if subchild.tag == 'EventN':
                #print subchild.tag, subchild.text
                event = {subchild.tag : int(subchild.text)}
                #print event
            if subchild.tag == 'TriggerN':
                #print subchild.tag, subchild.text
                trigger = {subchild.tag : int(subchild.text)}
                #print trigger
            if subchild.tag == 'Timestamp' and subindex == 9:
                #print subindex, subchild.tag, subchild.text.split('  ->  ')
                timestamp = {subchild.tag : subchild.text.split('  ->  ')}
                #print timestamp
        event.update(trigger)
        event.update(timestamp)
        data = data.append(event, ignore_index=True)
        if index > max_event:
            break
    return data

def xml2dfv3(filename, max_event):
    tree = ET.parse(filename)
    print "... parsing done"
    root = tree.getroot()
    print "... getroot done"
    #data = pd.DataFrame(columns=['EventN', 'TriggerN', 'Timestamp'])
    data = np.zeros(0, dtype={
        'names':['EventN', 'TriggerN', 'Timestamp'],
        'formats':['uint32', 'uint32', '2uint32']})
    #print data, data.dtype
    for index, child in enumerate(root):
        #print index, child.tag, child.text
        event = 0.
        trigger = 0.
        timestamp = [0., 0.]
        #print child[11][1].tag
        for subindex, subchild in enumerate(child[11][1]):
            #print subindex, subchild.tag, subchild.text
            if subchild.tag == 'EventN':
                #print subchild.tag, subchild.text
                event = int(subchild.text)
                #print event
            if subchild.tag == 'TriggerN':
                #print subchild.tag, subchild.text
                trigger = int(subchild.text)
                #print trigger
            if subchild.tag == 'Timestamp' and subindex == 9:
                #print subindex, subchild.tag, subchild.text.split('  ->  ')
                timestamp[0] = int(subchild.text.split('  ->  ')[0])
                timestamp[1] = int(subchild.text.split('  ->  ')[1])
                #print timestamp
        #event.update(trigger)
        #event.update(timestamp)
        data = np.append(data, np.array([(event, trigger, timestamp)], dtype=data.dtype))
        #print data
        if index > max_event:
            break
    return data

if __name__ == "__main__":
    arguments = docopt(__doc__, version='convert from xml to df/np')
    filename = arguments['--input']
    print filename

    data = xml2dfv3(filename, int(arguments['--max_event']))
    print data
    np.save(filename[:-4], data)
