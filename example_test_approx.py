import json
import FeatureWindow as fw
import matplotlib.pyplot as plt
import numpy as np
import math
import sys

KEY = '192.168.2.108_1'
KEY = '192.168.2.110_114.114.114.114_1'

TAU_100 = 100.0
TAU_10 = 10.0
TAU_1 = 1.0
TAU_01 = 0.1


timevalues_path = "json_data_ok_all.json" #the .json file to process
#timevalues_path = "json_data.json" #the .json file to process
#stats_path = "json_stats.json"
stats_path = "json_stats_ok_all.json"

timevalues_dict = dict()
with open(timevalues_path, "r") as read_content:
   timevalues_dict=json.load(read_content)

stats_dict = dict()
with open(stats_path, "r") as read_content:
   stats_dict=json.load(read_content)

flow_type = 'source'
# flow_type = 'sourcedest'
# flow_type = 'conversation'

flow_number = 1

key =stats_dict[flow_type]['list'][flow_number][1]

print (key)
print (len(timevalues_dict[key]))

# # CONFIGURATION USED FOR rate_10_100_ewma.png
# use_tau = [TAU_10, TAU_100]
# START = 0
# DURATION = 420
# LEGEND = [r'$\tau$=10 [s]', r'$\tau$=100 [s]']

# # CONFIGURATION USED FOR rate_01_1_ewma.png
# use_tau = [TAU_01, TAU_1]
# START = 20
# DURATION = 12
# LEGEND = [r'$\tau$=0.1 [s]', r'$\tau$=1 [s]']

use_tau = [TAU_01, TAU_1, TAU_10, TAU_100]
use_tau = [TAU_10, TAU_100]
use_tau = [TAU_01, TAU_1, TAU_10]
# use_tau = [TAU_1, TAU_10]
# use_tau = [TAU_01]
use_tau = [TAU_01, TAU_1, TAU_10, TAU_100]
use_tau = [TAU_10, TAU_100]

use_tau = [TAU_01, TAU_1]
use_tau = [TAU_10]
use_tau = [TAU_01]

START = 20
DURATION = 40
#LEGEND = [r'$\tau$=0.1 [s]', r'$\tau$=1 [s]']
LEGEND = [r'$\tau$=10 [s]']
LEGEND = [r'$\tau$=1 [s]']


def plot_pkt_rate (start, duration) :
    for i in range (len(use_tau)) :
        times = np_ewma_times
        values = rate_estimate_list[i]
        values = np.divide(values, use_tau[i])
        times, values = timestamped_list.time_slice(times,values, start_time=start,
                                            duration = duration)
        plt.plot (times, values)

#COLORS = ['red','blue','green','black']

def plot_bw (start, duration) :
    for i in range (len(use_tau)) :
        times = np_ewma_times
        values = ewma_bytes_list[i]
        values = np.divide(values, use_tau[i])
        times, values = timestamped_list.time_slice(times,values, start_time=start,
                                            duration = duration)
        plt.plot(times, values)

def plot_pckt_count (start, duration) :
    for i in range (len(use_tau)) :
        times = np_ewma_times
        values = ewma_pckt_list[i]
        values = np.divide(values, (1 << 20))
        times, values = timestamped_list.time_slice(times,values, start_time=start,
                                            duration = duration)
        
        plt.plot(times, values)


timestamped_list = fw.TimestampedList()
for couple in timevalues_dict[key] :
   timestamped_list.append(fw.TimestampedClass(couple[0],couple[1]))

ewma_times=[]
ewma_bytes_list=[]
ewma_pckt_list=[]
rate_estimate_list=[] #currently rate estimate is the same as ewma_pckt_list


for i in range (len(use_tau)) :
    ewma_times=[]
    new_list_bytes = list()
    new_list = list()

    ewma_bytes_list.append(new_list_bytes)
    ewma_pckt_list.append(new_list)
    timestamped_list.eval_approx(use_tau[i], times=ewma_times, approx_bytes=new_list_bytes, approx_pckt=new_list)
    #timestamped_list.decay_values(use_tau[i], times=ewma_times, ewma_values=new_list_bytes, ewma_rate_values=new_list)



np_ewma_times = np.asarray(ewma_times)
np_ewma_times = np_ewma_times - ewma_times[0]

for i in range (len(use_tau)) :
    new_list = list()
    rate_estimate_list.append(new_list)
    for j in range(len(ewma_pckt_list[i])) :
        #CURRENTLY THIS IS NOT NEEDED
        #AS EACH VALUE w IS ONLY COPIED
        w = ewma_pckt_list[i][j]
        new_list.append(w) #mytest
        # if w <= 1 :
        #     new_list.append (0)
        # else :
        #     T = - use_tau[i] * math.log(1.0 - 1.0/w)
        #     new_list.append(1/T)

# # PLOT PACKET RATE
# plot_pkt_rate(START, DURATION)
# plt.xlabel('Timestamp [s]')
# plt.ylabel('Pakets/s')
# plt.title(r'Packet rate in time window $\tau$ (EWMA)')
# plt.legend(LEGEND,loc='upper left')

# # PLOT BW
# plot_bw(START, DURATION)
# plt.xlabel('Timestamp [s]')
# plt.ylabel('Rate [Bytes/s]')
# plt.title(r'Throughput in time window $\tau$ (EWMA)')
# plt.legend(LEGEND,loc='upper left')


# PLOT PACKET COUNT
plot_pckt_count(START, DURATION)
plt.xlabel('Timestamp [s]')
plt.ylabel('Packets')
plt.title(r'Packets in time window $\tau$ (approx)')
plt.legend(LEGEND,loc='upper left')


# timestamped_list.process_all(use_tau)

# # timestamped_list.print_sorted_list()

# my_times=[]
# my_values=[]


# timestamped_list.get_time_values(times=my_times,values=my_values )
# timestamped_list.sample_and_hold(times=my_times,values=my_values)

# np_times = np.asarray(my_times)
# np_times = np_times - my_times[0]



#plt.plot(np_times,my_values)

# #  
# flow_type = 'conversation'
# flow_number = 12
#plt.plot(np_times[6800:6835],my_values[6800:6835])
# plt.plot(np_times[6799:6839],my_values[6799:6839])
