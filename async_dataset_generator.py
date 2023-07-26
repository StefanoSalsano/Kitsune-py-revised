'''
Run feature extraction on the entire trace and save the asynchronous dataset.

At each packet, save the features belonging to each different flow in a LRUCache
object, named "lru_controller", with the flow ID as the key.

Maintain another dict named "switch" that gets updated at fixed
time intervals, by copying the lru_controller object into it. The time interval
is calculated using the timestamp of the packet being processed.

When a packet is processed, give it the features of its related flows from the
switch dict. If the flow is not in the switch object, give it the
featues initialised to 1, as if it were a new flow.

for LRU sync case: update Afterimage.py > incStatDB > register/register_cov

for LRU async case: consider delay in transmitting updated LRU to switch

add keys to return vector in netStat.py > netStat > updateGetStats
'''

from lru import LRU
from FeatureExtractor import *
import numpy as np
import argparse

def compare_exact(first, second):
    """Return whether two dicts of arrays are exactly equal"""
    if first.keys() != second.keys():
        return False
    return all(np.array_equal(first[key], second[key]) for key in first)


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', help="input file path")
parser.add_argument('-o', help="output file path")
parser.add_argument('-n', help="number of elements saved in the LRU cache")
parser.add_argument('-t', default=0.1, type=float, help="LRU cache update interval")
parser.add_argument('-d', default=0.03, type=float, help="LRU cache update delay")
args = parser.parse_args()



PATH_IN = args.i #the pcap, pcapng, or tsv file to process.
PATH_OUT = args.o

LIMIT = np.Inf #the number of packets to process


i = 0
lru_controller = LRU(int(args.n))
ctr = dict()
db_init_count = 0
lru_init_count = 0

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
        # unpack features
        Hstat = features[:15]
        MIstat = features[15:30]
        HHstat = features[30:65]
        HHstat_jit = features[65:80]
        HpHpstat = features[80:115]
        timestamp, srcIP, dstIP, srcMAC, dstMAC, srcProtocol, dstProtocol, pkt_len = features[115:]

        timestamp = float(timestamp)
        pkt_len = int(pkt_len)

        # flow counter using dict
        ctr[srcIP] = 1
        ctr[srcMAC+'_'+srcIP] = 1
        ctr[srcIP+'_'+dstIP] = 1
        ctr[srcIP+'_'+dstIP+'_jit'] = 1
        if srcProtocol == 'arp':
            ctr[srcMAC+'_'+dstMAC] = 1
        else:
            ctr[srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol] = 1

        # update lru_controller
        lru_controller[srcIP] = Hstat
        lru_controller[srcMAC+'_'+srcIP] = MIstat
        lru_controller[srcIP+'_'+dstIP] = HHstat
        lru_controller[srcIP+'_'+dstIP+'_jit'] = HHstat_jit
        if srcProtocol == 'arp':
            lru_controller[srcMAC+'_'+dstMAC] = HpHpstat
        else:
            lru_controller[srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol] = HpHpstat

        # check timestamp
        if i == 1:
            switch_new = dict(lru_controller.items())
            switch_cur = dict()
            prev_timestamp = timestamp
        
        if timestamp - prev_timestamp > args.t:
            # case in which more than t - d have passed since last packet
            if not compare_exact(switch_cur, switch_new):
            # if switch_cur != switch_new:
                # update switch_cur
                switch_cur = switch_new

            # update switch_new
            switch_new = dict(lru_controller.items())
            prev_timestamp = timestamp
        elif timestamp - prev_timestamp > args.d:
            # update switch_cur
            switch_cur = switch_new

        # count new flows
        if Hstat[0] == '1.0':
            db_init_count +=1
        if MIstat[0] == '1.0':
            db_init_count +=1
        if HHstat[0] == '1.0':
            db_init_count +=1
        if HHstat_jit[0] == '1.0':
            db_init_count +=1
        if HpHpstat[0] == '1.0':
            db_init_count +=1
        
        # get features from switch_cur and write them to file
        # if features are not in switch_cur, initialise them to 1st packet
        # count new flows
        if srcIP in switch_cur:
            Hstat = switch_cur[srcIP]
        else:
            Hstat = np.array([1, pkt_len, 0]*5)
            lru_init_count += 1
        if srcMAC+'_'+srcIP in switch_cur:
            MIstat = switch_cur[srcMAC+'_'+srcIP]
        else:
            MIstat = np.array([1, pkt_len, 0]*5)
            lru_init_count += 1
        if srcIP+'_'+dstIP in switch_cur:
            HHstat = switch_cur[srcIP+'_'+dstIP]
        else:
            HHstat = np.array([1, pkt_len, 0, pkt_len, 0, 0, 0]*5)
            lru_init_count += 1
        if srcIP+'_'+dstIP+'_jit' in switch_cur:
            HHstat_jit = switch_cur[srcIP+'_'+dstIP+'_jit']
        else:
            HHstat_jit = np.array([1, 0, 0]*5)
            lru_init_count += 1
        if srcProtocol == 'arp':
            if srcMAC+'_'+dstMAC in switch_cur:
                HpHpstat = switch_cur[srcMAC+'_'+dstMAC]
            else:
                HpHpstat = np.array([1, pkt_len, 0, pkt_len, 0, 0, 0]*5)
                lru_init_count += 1
        else:
            if srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol in switch_cur:
                HpHpstat = switch_cur[srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol]
            else:
                HpHpstat = np.array([1, pkt_len, 0, pkt_len, 0, 0, 0]*5)
                lru_init_count += 1
        # combine in one vector
        features = np.concatenate((Hstat, MIstat, HHstat, HHstat_jit, HpHpstat))
        # write to file
        out_file.write(','.join(map(str, features)) + '\n')

# final count
print(f"flow count: {len(ctr)}")
print(f"db init count: {db_init_count}")
print(f"lru init count: {lru_init_count}")
