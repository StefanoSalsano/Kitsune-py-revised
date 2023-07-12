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

TODO: check how to handle the jitter on the first packet.

for LRU sync case: update Afterimage.py > incStatDB > register/register_cov

for LRU async case: consider delay in transmitting updated LRU to switch

add keys to return vector in netStat.py > netStat > updateGetStats
'''

from lru import LRU
from FeatureExtractor import *
import numpy as np


PATH_IN = "Mirai2000.pcap" #the pcap, pcapng, or tsv file to process.
PATH_OUT = "Mirai2000.csv"

LIMIT = np.Inf #the number of packets to process


i = 0
lru_controller = LRU(100)

# init feature extractor
extractor = FE(PATH_IN, LIMIT)
with open(PATH_OUT, 'w') as out_file:
    while True:
        i += 1
        if i % 1000 == 0:
            print(i)
        # get next features vector
        features = extractor.get_next_vector()
        # unpack features
        Hstat = features[:3]
        MIstat = features[3:6]
        HHstat = features[6:13]
        HHstat_jit = features[13:16]
        HpHpstat = features[16:23]
        timestamp, srcIP, dstIP, srcMAC, dstMAC, srcProtocol, dstProtocol = features[23:]

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
        
        if timestamp - prev_timestamp > 0.1:
            # # unlikely case in which more than 0.07s have passed since last packet
            # if switch_cur != switch_new:
            #     # update switch_cur
            #     switch_cur = switch_new

            # update switch_new
            switch_new = dict(lru_controller.items())
            prev_timestamp = timestamp
        elif timestamp - prev_timestamp > 0.03:
            # update switch_cur
            switch_cur = switch_new
        
        # get features from switch_cur and write them to file
        if srcIP in switch_cur:
            Hstat = switch_cur[srcIP]
        else:
            

        if len(features) == 0:
            break # no packets left