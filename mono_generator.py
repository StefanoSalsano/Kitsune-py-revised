from lru import LRU
from FeatureExtractor import *
import numpy as np
import pandas as pd
import argparse

def compare_exact(first, second):
    """Return whether two dicts of arrays are exactly equal"""
    if first.keys() != second.keys():
        return False
    return all(np.array_equal(first[key], second[key]) for key in first)


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-p', choices=[1, 5, 10, 25, 50, 100], type=int, help="percentage of elements saved in the LRU cache", required=True)
parser.add_argument('-t', default=0.1, type=float, help="LRU cache update interval")
parser.add_argument('-d', default=0, type=float, help="LRU cache update delay")
parser.add_argument('--no-delay', action="store_true", help="do not consider any delay")
args = parser.parse_args()

LIMIT = np.Inf #the number of packets to process
LABELS = "../datasets/kitsune/labels_all_cls.csv"
DATASETS = {
    "Active_Wiretap": ["pcapng", 229],
    "ARP_MitM": ["pcapng", 742],
    "Fuzzing": ["pcapng", 1863],
    "Mirai": ["pcap", 56261],
    "SSDP_Flood": ["pcap", 66847]
}
############## prova
# DATASETS = {
#     "ARP_MitM": ["pcapng", 229]
# }
##################

extracted_data = list()
path_out = f"../datasets/kitsune/dataset_lru_{args.p}_{int(args.t*1000)}_{int(args.d*1000)}.csv"

# process one dataset at a time
for dataset, pcap_num in DATASETS.items():
    i = 0
    ctr = dict()
    print(f"processing dataset: {dataset}")
############## prova
    path_in = f"../datasets/kitsune/{dataset}_pcap.{pcap_num[0]}.tsv"
    # path_in = f"../datasets/kitsune/{dataset}_pcap9.{pcap_num[0]}.tsv"
##################
    path_tmp = f"../datasets/kitsune/{dataset}_tmp_{args.p}_{int(args.t*1000)}_{int(args.d*1000)}.csv"
    lru_size = round(pcap_num[1] * args.p / 100)
    lru_controller = LRU(lru_size)

    # init feature extractor
    extractor = ""
    extractor = FE(path_in, LIMIT)
    print(extractor.nstat.HT_H.HT)
    with open(path_tmp, 'w') as file_tmp:
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
            # ctr[srcIP] = 1
            # ctr[srcMAC+'_'+srcIP] = 1
            # ctr[srcIP+'_'+dstIP] = 1
            # ctr[srcIP+'_'+dstIP+'_jit'] = 1
            # if srcProtocol == 'arp':
            #     ctr[srcMAC+'_'+dstMAC] = 1
            # else:
            #     ctr[srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol] = 1

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
            if args.no_delay: # use the lru right away
                switch_cur = dict(lru_controller.items())
            else:
                if i == 1:
                    if args.d == 0:
                        switch_new = ""
                        switch_cur = dict(lru_controller.items())
                    else:
                        switch_new = dict(lru_controller.items())
                        switch_cur = dict()
                    prev_timestamp = timestamp
                
                if timestamp - prev_timestamp > args.t:
                    # delay is 0, avoid 1 copy
                    if args.d == 0:
                        switch_cur = dict(lru_controller.items())
                    else:
                        # case in which more than t - d have passed since last packet
                        if not compare_exact(switch_cur, switch_new):
                            # update switch_cur
                            switch_cur = switch_new
                        # update switch_new
                        switch_new = dict(lru_controller.items())
                        prev_timestamp = timestamp
                elif timestamp - prev_timestamp > args.d:
                    # update switch_cur
                    switch_cur = switch_new

            # get features from switch_cur and write them to file
            # if features are not in switch_cur, initialise them to 1st packet
            # count new flows
            if srcIP in switch_cur:
                Hstat = switch_cur[srcIP]
            else:
                Hstat = np.array([1, pkt_len, 0]*5)
            if srcMAC+'_'+srcIP in switch_cur:
                MIstat = switch_cur[srcMAC+'_'+srcIP]
            else:
                MIstat = np.array([1, pkt_len, 0]*5)
            if srcIP+'_'+dstIP in switch_cur:
                HHstat = switch_cur[srcIP+'_'+dstIP]
            else:
                HHstat = np.array([1, pkt_len, 0, pkt_len, 0, 0, 0]*5)
            if srcIP+'_'+dstIP+'_jit' in switch_cur:
                HHstat_jit = switch_cur[srcIP+'_'+dstIP+'_jit']
            else:
                HHstat_jit = np.array([1, 0, 0]*5)
            if srcProtocol == 'arp':
                if srcMAC+'_'+dstMAC in switch_cur:
                    HpHpstat = switch_cur[srcMAC+'_'+dstMAC]
                else:
                    HpHpstat = np.array([1, pkt_len, 0, pkt_len, 0, 0, 0]*5)
            else:
                if srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol in switch_cur:
                    HpHpstat = switch_cur[srcIP +'_'+ srcProtocol+'_'+dstIP +'_'+ dstProtocol]
                else:
                    HpHpstat = np.array([1, pkt_len, 0, pkt_len, 0, 0, 0]*5)
            # combine in one vector
            features = np.concatenate((Hstat, MIstat, HHstat, HHstat_jit, HpHpstat))
            # append to list
            # extracted_data.append(list(features))
            # write to file
            file_tmp.write(','.join(map(str, features)) + '\n')

    # final count
    # print(f"flow count: {len(ctr)}")

# free up memory
extracted_data = ""

# rebuild dataframe
df = None
for dataset in DATASETS.keys():
    path_tmp = f"../datasets/kitsune/{dataset}_tmp_{args.p}_{int(args.t*1000)}_{int(args.d*1000)}.csv"
    df = pd.read_csv(path_tmp, header=None)
    if df is None:
        df = pd.read_csv(path_tmp, header=None)
    else:
        df = pd.concat([df, pd.read_csv(path_tmp, header=None)], ignore_index=True, axis=0, join='outer')
df = df.astype(float)


# print(df)

# normalization
max_row = []
print("Normalizing dataframe")
for column in df.columns:
    max = df[column].abs().max()
    df[column] = 0 if max == 0 else df[column] / df[column].abs().max()

# print(df)

# add labels
print("adding labels")
labels = pd.read_csv(LABELS, header=None)
labels.columns = ["ok", "arp", "ssdp", "mirai", "wtap", "fuzz"]
labels = labels.astype(int)
df = df.join(labels)
# free up memory
labels = ""

# print(df)

print("select test rows")
# read test index list
with open("test_index_list.csv", "r") as in_file:
    reader = csv.reader(in_file)
    index_list = list(reader)
index_list = pd.Index(index_list[0])
# df = df[df.index.isin(index_list)]
df = df.iloc[index_list]

# print(df)

print("writing to file...")
df.to_csv(path_out, header=None, index=True)