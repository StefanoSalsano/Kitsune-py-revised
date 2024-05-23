import json
import FeatureWindow as fw
import matplotlib.pyplot as plt
import numpy as np

KEY = '192.168.2.108_1'
KEY = '192.168.2.110_114.114.114.114_1'

TAU_100 = 100.0
TAU_10 = 10.0
TAU_1 = 1.0
TAU_01 = 0.1

#path = "json_data_ok_all.json" #the .json file to process
timevalues_path = "json_data_ok_all.json"
#timevalues_path = "json_data.json" #the .json file to process
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

# flow_type = 'source'
# flow_number = 7

key =stats_dict[flow_type]['list'][flow_number][1]

print (key)
print (len(timevalues_dict[key]))

# # CONFIGURATION USED FOR rate_10_100_exact.png
# START = 0
# DURATION = 420
# use_tau = [TAU_10, TAU_100]
# SELECTED = [0,1]
# LEGEND = [r'$\tau$=10 [s]', r'$\tau$=100 [s]']

# use_tau = [TAU_01, TAU_1, TAU_10, TAU_100]
# SELECTED = [0,1,2,3]
# LEGEND = [r'$\tau$=0.1 [s]', r'$\tau$=1 [s]', r'$\tau$=10 [s]', r'$\tau$=100 [s]']

# CONFIGURATION USED FOR rate_01_1_exact.png
START = 20
DURATION = 12
use_tau = [TAU_01, TAU_1]
SELECTED = [0,1]
LEGEND = [r'$\tau$=0.1 [s]', r'$\tau$=1 [s]']



def plot_count (tau_index_list, start, duration) :
    for tau_index in tau_index_list :
        times = my_times_list[tau_index]
        values = my_count_val_list[tau_index]
        times, values = ts_list.time_slice(times,values, start_time=start,
                                        duration = duration)
        plt.plot(times, values)

def plot_avg_len (tau_index_list, start, duration) :
    for tau_index in tau_index_list :
        times = my_times_list[tau_index]
        values = my_len_val_list[tau_index]
        times, values = ts_list.time_slice(times,values, start_time=start,
                                        duration = duration)
        plt.plot(times, values)

def plot_pkt_rate (tau_index_list, start, duration) :
    for tau_index in tau_index_list :
        times = my_times_list[tau_index]
        values = my_count_val_list[tau_index]
        values = np.divide(values, use_tau[tau_index])
        times, values = ts_list.time_slice(times,values, start_time=start,
                                        duration = duration)
        plt.plot(times, values)


def plot_bw (tau_index_list, start, duration) :
    for tau_index in tau_index_list :
        times = my_times_list[tau_index]
        values = my_bw_values_list[tau_index]
        times, values = ts_list.time_slice(times,values, start_time=start,
                                        duration = duration)
        plt.plot(times, values)

my_times_list=[]
my_count_val_list=[]
my_len_val_list=[]
my_bw_values_list=[]

for i in range (len(use_tau)) :
    ts_list = fw.TimestampedList()
    time_origin = timevalues_dict[key][0][0]
    for couple in timevalues_dict[key] :
        ts_list.append(fw.TimestampedClass(couple[0]-time_origin,couple[1]))

    # ewma_times=[]
    # ewma_values=[]
    # ewma_rate_values=[]
    # timestamped_list.evaluate_ewma(use_tau, times=ewma_times, ewma_values=ewma_values, ewma_rate_values=ewma_rate_values)
    # np_ewma_times = np.asarray(ewma_times)
    # np_ewma_times = np_ewma_times - ewma_times[0]

    ts_list.process_all(use_tau[i])


    my_times_list.append(list())
    my_count_val_list.append(list())
    my_len_val_list.append(list())
    my_bw_values_list.append(list())

    # print ('use tau', use_tau[i])
    ts_list.get_time_values(times=my_times_list[i],count=my_count_val_list[i], avg_len= my_len_val_list[i], bw=my_bw_values_list[i])
    
    ts_list.sample_and_hold(times=my_times_list[i],count=my_count_val_list[i], avg_len= my_len_val_list[i], bw=my_bw_values_list[i])
    # np_times = np.asarray(my_times_list[i])
    # np_times = np_times - my_times_list[i][0]

    # if i == 1 :
    #     for j in range (len(my_count_val_list[i])) :
    #         timestamp = my_times_list[i][j] 
    #         boolean = timestamp > 4131 and timestamp < 4133
    #         if boolean : print (timestamp, my_count_val_list[i][j])




# flow_type = 'conversation'
# flow_number = 12
# Adding labels and title
# plt.xlabel('Timestamp [s]')
# plt.ylabel('Number of packets')
# plt.title(r'Packet count in time window $\tau$')
# plot_count([0,1],10,30)
# plt.legend([r'$\tau$=0.1 [s]', r'$\tau$=1 [s]'],loc='upper right')

# # PLOT COUNT FOR DIFFERENT TAU
# # Adding labels and title
# plt.xlabel('Timestamp [s]')
# plt.ylabel('Number of packets')
# plt.title(r'Packet count in time window $\tau$')
# #plt.ylim(bottom=0, top=140)
# plot_count([2,3],90,20)
# plt.legend([r'$\tau$=10 [s]', r'$\tau$=100 [s]'],loc='upper left')

# # PLOT BW
# # Adding labels and title
# plt.xlabel('Timestamp [s]')
# plt.ylabel('Bytes/s')
# plt.title(r'Bandwidth in time window $\tau$')
# #plt.ylim(bottom=0, top=140)
# #plot_count([2,3],START,DURATION)
# plot_bw([2,3],START,DURATION)
# plt.legend([r'$\tau$=10 [s]', r'$\tau$=100 [s]'],loc='upper left')

plt.xlabel('Timestamp [s]')

# # PLOT PACKET RATE
# # Adding labels and title
# plt.ylabel('Pakets/s')
# plt.title(r'Packet rate in time window $\tau$ (EXACT)')
# #plt.ylim(bottom=0, top=140)
# plot_pkt_rate(SELECTED,START,DURATION)
# plt.legend(LEGEND,loc='upper left')

# PLOT BW
plt.ylabel('Rate [Bytes/s]')
plt.title(r'Throughput in time window $\tau$ (EXACT)')
#plt.ylim(bottom=0, top=140)
plot_bw(SELECTED,START,DURATION)
plt.legend(LEGEND,loc='upper left')



# # flow_type = 'source'
# # flow_number = 7
# # Adding labels and title
# plt.xlabel('Timestamp [s]')
# plt.ylabel('Number of packets')
# plt.title(r'Packet count in time window $\tau$')
# plot_count([2,3],START,DURATION)
# plt.legend([r'$\tau$=10 [s]', r'$\tau$=100 [s]'],loc='upper left')

# # Adding labels and title
# plt.xlabel('Timestamp [s]')
# plt.ylabel('Number of packets')
# plt.title(r'Packet count in time window $\tau$')
# plot_count([0,1],START,DURATION)
# plt.legend([r'$\tau$=0.1 [s]', r'$\tau$=1 [s]'],loc='upper left')

# plt.xlabel('Timestamp [s]')
# plt.ylabel('Estimated pkt len [Bytes]')
# plt.title(r'Avg packet lenght in time window $\tau$')
# plt.ylim(bottom=0, top=150)
# plot_avg_len([2,3],START,DURATION)
# #plt.legend([r'$\tau$=10 [s]', r'$\tau$=100 [s]'],loc='upper left')



#plt.plot(np_times,my_values)

# #  
# flow_type = 'conversation'
# flow_number = 12
# plt.plot(my_times_list[0][6799:6839],my_count_val_list[0][6799:6839])
# plt.plot(my_times_list[0][6799:6839],my_bw_values_list[0][6799:6839])

#plt.plot(np_ewma_times[1700:1710], ewma_rate_values[1700:1710])
