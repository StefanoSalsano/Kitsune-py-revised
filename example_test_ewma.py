import json
import FeatureWindow as fw
import matplotlib.pyplot as plt
import numpy as np
import math

KEY = '192.168.2.108_1'
KEY = '192.168.2.110_114.114.114.114_1'

TAU_100 = 100.0
TAU_10 = 10.0
TAU_1 = 1.0
TAU_01 = 0.1

#path = "json_data_ok_all.json" #the .json file to process
timevalues_path = "json_data.json" #the .json file to process
stats_path = "json_stats.json"

timevalues_dict = dict()
with open(timevalues_path, "r") as read_content:
   timevalues_dict=json.load(read_content)

stats_dict = dict()
with open(stats_path, "r") as read_content:
   stats_dict=json.load(read_content)

flow_type = 'source'
flow_type = 'sourcedest'
flow_type = 'conversation'

flow_number = 12

key =stats_dict[flow_type]['list'][flow_number][1]

print (key)
print (len(timevalues_dict[key]))

use_tau = [TAU_01, TAU_1, TAU_10, TAU_100]

timestamped_list = fw.TimestampedList()
for couple in timevalues_dict[key] :
   timestamped_list.append(fw.TimestampedClass(couple[0],couple[1]))

ewma_times=[]
ewma_values=[]
ewma_rate_values_list=[]
rate_estimate_list=[]

for i in range (len(use_tau)) :
    ewma_times=[]
    new_list = list()
    ewma_rate_values_list.append(new_list)
    timestamped_list.evaluate_ewma(use_tau[i], times=ewma_times, ewma_values=ewma_values, ewma_rate_values=new_list)

np_ewma_times = np.asarray(ewma_times)
np_ewma_times = np_ewma_times - ewma_times[0]

for i in range (len(use_tau)) :
    new_list = list()
    rate_estimate_list.append(new_list)
    for j in range(len(ewma_rate_values_list[i])) :
        w = ewma_rate_values_list[i][j]
        if w <= 1 :
            new_list.append (0)
        else :
            T = - use_tau[i] * math.log(1.0 - 1.0/w)
            new_list.append(1/T)


# for i in range (len(use_tau)) :
#     plt.plot(np_ewma_times[1700:1710], ewma_rate_values_list[i][1700:1710])

for i in range (len(use_tau)) :
    plt.plot(np_ewma_times[1700:1710], rate_estimate_list[i][1700:1710])


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
