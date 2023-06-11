import json
import FeatureWindow as fw

KEY = '192.168.2.108_1'
KEY = '192.168.2.110_114.114.114.114_1'


path = "json_data_ok_all.json" #the .json file to process

my_dict = dict()
with open(path, "r") as read_content:
   my_dict=json.load(read_content)

print (len(my_dict[KEY]))

timestamped_list = fw.TimestampedList()
for couple in my_dict[KEY] :
   timestamped_list.append(fw.TimestampedClass(couple[0],couple[1]))

timestamped_list.process_all()

timestamped_list.print_sorted_list()
