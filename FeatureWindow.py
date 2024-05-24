import datetime
import random
import math
import numpy as np

TIMESLOT_DURATION = 100000*1000  # 0.1 second in nanoseconds
TIMESLOT_DURATION = 5000000*1000  # 5 second in nanoseconds
TIMESLOT_DURATION = 500000*1000  # 0.5 second in nanoseconds

LOG_SCALE_FACTOR = 20
MAX_DELTA = 10

def scale (value) :
    return value << LOG_SCALE_FACTOR

def unscale (value) :
    # return ((value+(1<<(LOG_SCALE_FACTOR-1)))  >> LOG_SCALE_FACTOR)
    return (value >> LOG_SCALE_FACTOR)

def evaluate_decay_table (tau, number_of_slots) :
    decay_table = []
    for i in range(number_of_slots):
        decay = math.exp(-i*TIMESLOT_DURATION/tau)
        decay_table.append(decay)
    return decay_table

def evaluate_exponential_fixed_point(k_max, tau_over_t, log_scale_factor):
    results = []
    for k in range(0, k_max + 1):
        argument = k / tau_over_t
        result = math.exp(-argument) << log_scale_factor
        rounded_result = round(result)
        results.append(rounded_result)
    return results


class TimestampedClass:
    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value
        self.avg_bw_last_t_window = None
        self.avg_len_last_t_window = None
        self.count_last_t = None
        self.ewma = None  #average packet size???? no, byte counter
        self.ewma_rate = None #packet counter
        self.approx_pckt = 0
        self.approx_bytes = 0
        self.slot = 0  # slot number
        self.pckt_in_slot = 0
        self.bytes_in_slot = 0

    def get_timestamp(self):
        return self.timestamp

    def get_value(self):
        return self.value

    def set_avg_bw_last_t_window(self, avg):
        self.avg_bw_last_t_window = avg

    def get_avg_bw_last_t_window(self):
        return self.avg_bw_last_t_window

    def set_avg_len_last_t_window(self, avg_len):
        self.avg_len_last_t_window = avg_len

    def get_avg_len_last_t_window(self):
        return self.avg_len_last_t_window

    def set_ewma(self, ewma):
        self.ewma = ewma

    def get_ewma(self):
        return self.ewma

    def set_ewma_rate(self, ewma_rate):
        self.ewma_rate = ewma_rate

    def get_ewma_rate(self):
        return self.ewma_rate

    def set_count_last_t(self, count_last_t):
        self.count_last_t = count_last_t

    def get_count_last_t(self):
        return self.count_last_t

    def set_approx_pckt(self, approx_pckt):
        self.approx_pckt = approx_pckt

    def get_approx_pckt(self):
        return self.approx_pckt

    def set_approx_bytes(self, approx_bytes):
        self.approx_bytes = approx_bytes

    def get_approx_bytes(self):
        return self.approx_bytes

    def set_slot(self, slot):
        self.slot = slot

    def get_slot(self):
        return self.slot

    def set_pckt_in_slot(self, pckt_in_slot):
        self.pckt_in_slot = pckt_in_slot

    def get_pckt_in_slot(self):
        return self.pckt_in_slot

    def set_bytes_in_slot(self, bytes_in_slot):
        self.bytes_in_slot = bytes_in_slot

    def get_bytes_in_slot(self):
        return self.bytes_in_slot


def get_slot_from_time(time):
    time_nano = time*1000000*1000
    slot= int(time_nano/TIMESLOT_DURATION)
    return slot

class TimestampedList:
    def __init__(self):
        self.timestamped_list = []
        self.bytes_in_window = 0
        self.pkt_in_window = 0

    def get_element (self, index) :
        return self.timestamped_list[index]

    def process_next(self,i,tau) :
        """
        evaluate the exact window based features for a single packet
        """
        obj = self.timestamped_list[i]
        value = obj.get_value()
        timestamp = obj.get_timestamp()
        self.bytes_in_window += value
        # delta = timestamp - self.timestamped_list[0].get_timestamp()
        # boolean = delta > 4131 and delta < 4133
        if  value > 0 :
            self.pkt_in_window += 1
            decrease = TimestampedClass (timestamp+tau,-value)
            self.insert(decrease,start_from=i)
        else :
            self.pkt_in_window -= 1
        obj.set_avg_bw_last_t_window((float(self.bytes_in_window))/tau)
        obj.set_count_last_t(self.pkt_in_window)
        if self.pkt_in_window > 0 :
            obj.set_avg_len_last_t_window((float(self.bytes_in_window))/self.pkt_in_window)
        else :
            obj.set_avg_len_last_t_window = 0
        # if boolean : print (tau, delta, value, self.pkt_in_window )
        
    def process_all (self, window) :
        """
            evaluate the exact window based features for all packets
        """
        i = 0
        while (i < len(self.timestamped_list)) :
            self.process_next(i, window) 
            i += 1 

    def insert(self, obj, start_from=0):
        for i in range(start_from,len(self.timestamped_list)):
            if obj.get_timestamp() <= self.timestamped_list[i].get_timestamp():
                self.timestamped_list.insert(i, obj)
                break
        else:
            self.timestamped_list.append(obj)

    def insert_random(self, n, T):
        current_time = datetime.datetime.now()

        for _ in range(n):
            timestamp_diff = datetime.timedelta(microseconds=random.uniform(0, T))
            timestamp = current_time - timestamp_diff  # Reverse the order to evaluate previous T microseconds
            value = random.randint(1, 100)
            obj = TimestampedClass(timestamp, value)
            self.insert(obj)

    def append(self, obj):
        self.timestamped_list.append(obj)

    def print_sorted_list(self, range = []):
        for obj in self.timestamped_list:
            print(f"Tstamp: {obj.get_timestamp()}, Val: {obj.get_value()}, Avg T Win: {obj.get_avg_bw_last_t_window()}, EWMA: {obj.get_ewma()}")

    def get_time_values(self, times=[], count=[], avg_len=[], bw=[]):
        """
        extract the timestamps and the values of avg bw, count, avg len
        """
        for obj in self.timestamped_list:
            
            # timestamp = obj.get_timestamp()
            # delta = timestamp - self.timestamped_list[0].get_timestamp()
            # boolean = delta > 4131 and delta < 4133
            # if boolean : print ( delta, obj.get_count_last_t() )

            times.append (obj.get_timestamp())
            bw.append (obj.get_avg_bw_last_t_window())
            avg_len.append (obj.get_avg_len_last_t_window())
            count.append (obj.get_count_last_t())

    # def evaluate_average_previous_T(self, T):
    #     for i in range(len(self.timestamped_list)):
    #         current_time = self.timestamped_list[i].get_timestamp()
    #         start_time = current_time - datetime.timedelta(microseconds=T)

    #         total_value = 0
    #         count = 0

    #         for j in range(i, -1, -1):
    #             obj = self.timestamped_list[j]

    #             if obj.get_timestamp() >= start_time:
    #                 total_value += obj.get_value()
    #                 count += 1
    #             else:
    #                 break

    #         if count > 0:
    #             average = total_value / count
    #             self.timestamped_list[i].set_avg_last_t_window(average)
    #         else:
    #             self.timestamped_list[i].set_avg_last_t_window(0)  # Set average to 0 if no elements within the specified time range




    def evaluate_ewma(self, tau, times = [], ewma_bytes=[], ewma_pckt=[] ):
        """
        evaluate the packet rate
        note that ewma_pckt and ewma_bytes are actually counters, 
        which are then used to evaluate the rate dividing by tau
        """

        if not self.timestamped_list:
            return

        self.timestamped_list[0].set_ewma(self.timestamped_list[0].get_value())
        self.timestamped_list[0].set_ewma_rate(1)
        times.append(self.timestamped_list[0].get_timestamp())
        ewma_bytes.append (self.timestamped_list[0].get_value())
        ewma_pckt.append (1)

        for i in range(1, len(self.timestamped_list)):
            value = self.timestamped_list[i].get_value()
            time = self.timestamped_list[i].get_timestamp()
            slot = get_slot_from_time(time)
            # print (time, slot)
            prev_ewma = self.timestamped_list[i - 1].get_ewma()
            prev_ewma_rate = self.timestamped_list[i - 1].get_ewma_rate()
            prev_time = self.timestamped_list[i - 1].get_timestamp()
            decay = math.exp(-(time-prev_time)/tau)
            # ewma =  value/tau * (1-decay) + prev_ewma * decay
            #ewma =  value * (1-decay) + prev_ewma * decay
            ewma = value + decay * prev_ewma
            ewma_rate =  1 + prev_ewma_rate * decay

            self.timestamped_list[i].set_ewma(ewma)
            self.timestamped_list[i].set_ewma_rate(ewma_rate)
            times.append(time)
            ewma_bytes.append (ewma)
            ewma_pckt.append (ewma_rate)

    def eval_approx(self, tau, times = [], approx_bytes=[], approx_pckt=[] ):
        """
        approximate the packet and byte counters
        decay_table is a table of decay factors for each slot
        decay_table[0] is never used

        """
        def decay_table (delta) :
            return [1048576,
                    635993,
                    385750,
                    233969,
                    141909,
                    86072,
                    52206,
                    31664,
                    19205,
                    11649,
                    7065,
                    ][delta]

        if not self.timestamped_list:
            return

        #initialize estimate with 0
        self.timestamped_list[0].set_approx_pckt(0)
        self.timestamped_list[0].set_approx_bytes(0)
        slot = get_slot_from_time(self.timestamped_list[0].get_timestamp())
        #self.timestamped_list[0].set_slot(slot)
        pckt_in_slot = 1
        bytes_in_slot = self.timestamped_list[0].get_value()

        #self.timestamped_list[0].set_pckt_in_slot(1)
        #self.timestamped_list[0].set_bytes_in_slot(self.timestamped_list[0].get_value())

        times.append(self.timestamped_list[0].get_timestamp())
        approx_pckt.append(0)
        approx_bytes.append(0)

        for i in range(1, len(self.timestamped_list)):
            value = self.timestamped_list[i].get_value()
            time = self.timestamped_list[i].get_timestamp()

            flag = False
            if (time - self.timestamped_list[0].get_timestamp() > 20.5 and 
                time - self.timestamped_list[0].get_timestamp() < 45 ) :
                # print (time - self.timestamped_list[0].get_timestamp())
                flag = True

            prev_approx_pckt = self.timestamped_list[i - 1].get_approx_pckt()
            prev_approx_bytes = self.timestamped_list[i - 1].get_approx_bytes()

            new_slot = get_slot_from_time(time)
            if new_slot == slot:
                # self.timestamped_list[i].set_slot(new_slot)
                pckt_in_slot = pckt_in_slot + 1
                bytes_in_slot = bytes_in_slot + value

                #if flag : print (pckt_in_slot)

                self.timestamped_list[i].set_approx_pckt(prev_approx_pckt)
                self.timestamped_list[i].set_approx_bytes(prev_approx_bytes)

                approx_pckt.append(prev_approx_pckt)
                approx_bytes.append(prev_approx_bytes)

                # if flag : 
                #     print ("prev_approx_pckt", prev_approx_pckt)


            else:
                # new slot
                delta = new_slot - slot
                # print (pckt_in_slot, bytes_in_slot, delta)
                # if flag : 
                #     print ("new_slot",pckt_in_slot, unscale(prev_approx_pckt), delta)
                if delta <= MAX_DELTA:
                    # avg = (((((pckt_in_slot << LOG_SCALE_FACTOR) * decay_table(delta - 1))+(1 <<19) )>> LOG_SCALE_FACTOR) + 
                    #         (((prev_approx_pckt * decay_table(delta)) >> LOG_SCALE_FACTOR)+(1 <<19) ) )
                    avg = (unscale(scale(pckt_in_slot) * decay_table(delta - 1))  + 
                           unscale(prev_approx_pckt * decay_table(delta)) )

                    # if flag : 
                    #     print ("AVG",avg, unscale(avg))
                    self.timestamped_list[i].set_approx_pckt(avg)
                    approx_pckt.append(avg)
                    # avg_bytes = ((((bytes_in_slot << LOG_SCALE_FACTOR) * decay_table(delta - 1)) >> LOG_SCALE_FACTOR )+
                    #             ((prev_approx_bytes * decay_table(delta)) >> LOG_SCALE_FACTOR) )
                    avg_bytes = (unscale(scale(bytes_in_slot) * decay_table(delta - 1))  + 
                                 unscale(prev_approx_bytes * decay_table(delta)) )
                    

                    self.timestamped_list[i].set_approx_bytes(avg_bytes)
                    #print (avg >> LOG_SCALE_FACTOR, avg_bytes >> LOG_SCALE_FACTOR)
                    approx_bytes.append(avg)

                else: 

                    self.timestamped_list[i].set_approx_pckt(0)
                    self.timestamped_list[i].set_approx_bytes(0)
                    approx_pckt.append(0)
                    approx_bytes.append(0)

                pckt_in_slot = 1
                bytes_in_slot = value


            times.append(time)
            slot = new_slot



    def sample_and_hold(self,times = [], count=[], avg_len=[], bw=[] ) :
        """
        if count (t)= A and count(t+1) = B, then add a new point count(t+1) = A
        for each point in the list, so that the plot is a step function
        which keeps the value of the previous point until the next point
        """
        i = 0 
        while (i < len(times)-1) :
            next_time = times[i+1]
            times.insert(i+1,next_time)
            count.insert(i+1,count[i])
            avg_len.insert(i+1,avg_len[i])
            bw.insert(i+1,bw[i])
            i += 2

    def decay_values(self,tau=1,times = [], ewma_values=[], ewma_rate_values=[] ) :
        """
        if value (t)= A and value(t+1) = B, then add a new point 
        value(t+1) = A*decay_factor((t+1)-t) 
        for each point in the list
        """
        i = 0 
        while (i < len(times)-1) :
            decay = math.exp(-(times[i+1]-times[i])/tau)
            next_time = times[i+1]
            times.insert(i+1,next_time)
            ewma_values.insert(i+1,ewma_values[i]*decay)
            ewma_rate_values.insert(i+1,ewma_rate_values[i]*decay)
            i += 2

    def time_slice(self, times = [], values = [], start_time=0.0, end_time=np.inf,
                   duration = np.inf, samples = np.inf) :
        out_times = []
        out_values = []
        if duration < np.inf :
            end_time = min(end_time,start_time+duration)
            #print (end_time)
        counter = 0
        for i in range(len(times)) :
            timestamp = times [i]
            # print (timestamp)
            if timestamp > end_time : 
                # print ('end_time')
                break
            if timestamp >= start_time :
                out_times.append(timestamp)
                out_values.append(values[i])
                counter +=1 
            if counter >= samples : 
                # print ('samples')
                break
        # print (out_times, out_values)
        return out_times, out_values


# Example usage
# timestamped_list = TimestampedList()

# # Insert 5 instances with random timestamps
# timestamped_list.insert_random(5, 500000)  # T = 500000 microseconds

# # Evaluate average value over the previous 300000 microseconds for each element
# timestamped_list.evaluate_average_previous_T(300000)

# # Evaluate EWMA with alpha = 0.5
# timestamped_list.evaluate_ewma(0.5)

# # Print the sorted list with evaluated averages and EWMA
# timestamped_list.print_sorted_list()
