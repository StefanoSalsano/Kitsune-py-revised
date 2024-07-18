'''
Run feature extraction on the entire trace and save the asynchronous dataset.

At each packet, save the features belonging to each different flow in a LRUCache
object, named "lru_switch", with the flow ID as the key.

Maintain another dict named "switch" that gets updated at fixed
time intervals, by copying the lru_switch object into it. The time interval
is calculated using the timestamp of the packet being processed.

When a packet is processed, give it the features of its related flows from the
switch dict. If the flow is not in the switch object, give it the
featues initialised to 1, as if it were a new flow.

for LRU sync case: update Afterimage.py > incStatDB > register/register_cov

for LRU async case: consider delay in transmitting updated LRU to switch

add keys to return vector in netStat.py > netStat > updateGetStats
'''

from FeatureExtractor import *
import numpy as np
import argparse

# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', help="input file path", required=True)
parser.add_argument('-o', help="output file path", required=True)
args = parser.parse_args()



PATH_IN = args.i #the pcap, pcapng, or tsv file to process.
PATH_OUT = args.o

LIMIT = np.inf #the number of packets to process


i = 0

# init feature extractor
extractor = FE(PATH_IN, LIMIT)
with open(PATH_OUT, 'w') as out_file:
    while True:
        i += 1
        if i % 10000 == 0:
            print(i)
        # get next features vector
        features = extractor.get_next_vector()
        if len(features) == 0:
            break # no packets left

        # select only features
        features = features[:115]
        # write to file
        out_file.write(','.join(map(str, features)) + '\n')