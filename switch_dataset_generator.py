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
from lru import LRU
import argparse

# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', help="input file path", required=True)
parser.add_argument('-o', help="output file path", required=True)
parser.add_argument('-n', type=int, help="number of elements saved in the LRU cache", required=True)
args = parser.parse_args()



PATH_IN = args.i #the pcap, pcapng, or tsv file to process.
PATH_OUT = args.o

LIMIT = np.Inf #the number of packets to process


i = 0
ctr = dict()
lru_switch = LRU(args.n)

# init feature extractor
extractor = FE(PATH_IN, LIMIT)
with open(PATH_OUT, 'w') as out_file:
    while True:
        i += 1
        if i % 10000 == 0:
            print(i)
        # get next features vector
        features = extractor.get_next_vector(lru=lru_switch)
        if len(features) == 0:
            break # no packets left

        # print(i)

        # if i < 1000 and i != 1:
        #     continue
        # print(i)
        # if i > 1010:
        #     break

        # unpack features
        # Hstat = features[:15]
        # MIstat = features[15:30]
        # HHstat = features[30:65]
        # HHstat_jit = features[65:80]
        # HpHpstat = features[80:115]
        # timestamp, srcIP, dstIP, srcMAC, dstMAC, srcProtocol, dstProtocol, pkt_len = features[115:]

        # # update lru_switch
        # lru_switch[srcIP] = 1
        # lru_switch[srcMAC+'_'+srcIP] = 1
        # lru_switch[srcIP+'_'+dstIP] = 1
        # lru_switch[dstIP+'_'+srcIP] = 1
        # lru_switch['jitter'+srcIP+'_'+dstIP] = 1
        # if srcProtocol == 'arp':
        #     lru_switch[srcMAC+'_'+dstMAC] = 1
        #     lru_switch[dstMAC+'_'+srcMAC] = 1
        # else:
        #     lru_switch[srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol] = 1
        #     lru_switch[dstIP +'_'+ dstProtocol+'_'+srcIP +'_'+ srcProtocol] = 1

        # flow counter using dict
        # ctr[srcIP] = 1
        # ctr[srcMAC+'_'+srcIP] = 1
        # ctr[srcIP+'_'+dstIP] = 1
        # ctr[dstIP+'_'+srcIP] = 1
        # ctr[srcIP+'_'+dstIP+'_jit'] = 1
        # if srcProtocol == 'arp':
        #     ctr[srcMAC+'_'+dstMAC] = 1
        #     ctr[dstMAC+'_'+srcMAC] = 1
        # else:
        #     ctr[srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol] = 1
        #     ctr[dstIP +'_'+ dstProtocol+'_'+srcIP +'_'+ srcProtocol] = 1

        # print(srcIP+'_'+dstIP, 'len', len(lru_switch))

        # select only features
        features = features[:115]
        # write to file
        out_file.write(','.join(map(str, features)) + '\n')

print(f"flow count: {len(ctr)}")
print(f"len(lru_switch): {len(lru_switch)}")