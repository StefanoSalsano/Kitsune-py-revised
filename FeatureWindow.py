import datetime
import random

class TimestampedClass:
    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value
        self.avg_bw_last_t_window = None
        self.avg_len_last_t_window = None
        self.ewma = None

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


class TimestampedList:
    def __init__(self):
        self.timestamped_list = []
        self.bytes_in_window = 0
        self.pkt_in_window = 0

    def process_next(self,i,tau) :
        obj = self.timestamped_list[i]
        value = obj.get_value()
        timestamp = obj.get_timestamp()
        self.bytes_in_window += value
        if  value > 0 :
            self.pkt_in_window += 1
            decrease = TimestampedClass (timestamp+tau,-value)
            self.insert(decrease,start_from=i)
        else :
            self.pkt_in_window -= 1
        obj.set_avg_bw_last_t_window((float(self.bytes_in_window))/tau)
        if self.pkt_in_window > 0 :
            obj.set_avg_len_last_t_window((float(self.bytes_in_window))/self.pkt_in_window)
        else :
            obj.set_avg_len_last_t_window = 0

    def process_all (self) :
        i = 0
        while (i < len(self.timestamped_list)) :
            self.process_next(i, 10) 
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
            print(f"Timestamp: {obj.get_timestamp()}, Value: {obj.get_value()}, Avg Last T Window: {obj.get_avg_bw_last_t_window()}, EWMA: {obj.get_ewma()}")

    def evaluate_average_previous_T(self, T):
        for i in range(len(self.timestamped_list)):
            current_time = self.timestamped_list[i].get_timestamp()
            start_time = current_time - datetime.timedelta(microseconds=T)

            total_value = 0
            count = 0

            for j in range(i, -1, -1):
                obj = self.timestamped_list[j]

                if obj.get_timestamp() >= start_time:
                    total_value += obj.get_value()
                    count += 1
                else:
                    break

            if count > 0:
                average = total_value / count
                self.timestamped_list[i].set_avg_last_t_window(average)
            else:
                self.timestamped_list[i].set_avg_last_t_window(0)  # Set average to 0 if no elements within the specified time range

    def evaluate_ewma(self, alpha):
        if not self.timestamped_list:
            return

        self.timestamped_list[0].set_ewma(self.timestamped_list[0].get_value())

        for i in range(1, len(self.timestamped_list)):
            value = self.timestamped_list[i].get_value()
            prev_ewma = self.timestamped_list[i - 1].get_ewma()
            ewma = alpha * value + (1 - alpha) * prev_ewma
            self.timestamped_list[i].set_ewma(ewma)


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
