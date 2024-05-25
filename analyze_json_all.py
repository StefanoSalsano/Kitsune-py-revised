"""
read the json file with the time values and create a json file
with the statistics
"""
import json
#   warning: the following file is written by the script
output_stats_path = "json_stats_ok_all.json"

timevalues_path = "json_data_ok_all.json"

# timevalues_path = "json_data.json"
timevalues_dict = dict()
with open(timevalues_path, "r") as read_content:
   timevalues_dict=json.load(read_content)

i = 0
stats = dict()
stats_dict = dict()
stats_dict['source'] = {'histo':{}, 'list':[]}
stats_dict['sourcedest'] = {'histo':{}, 'list':[]}
stats_dict['conversation'] = {'histo':{}, 'list':[]}

flow_type=''
for key in timevalues_dict :
    i += 1
    count = key.count("_")
    if count in stats :
        stats[count] += 1
    else :
        stats[count] = 1
    if count == 1 :
        flow_type = 'source'
    elif count == 2 :
        flow_type = 'sourcedest'
    elif count == 4 :
        flow_type = 'conversation'
    
    packets = len(timevalues_dict[key])
    if packets in stats_dict[flow_type]['histo'] :
        stats_dict[flow_type]['histo'][packets] += 1
    else :
        stats_dict[flow_type]['histo'][packets] = 1
    
    stats_dict[flow_type]['list'].append([packets, key])

stats_dict['source']['list'].sort(reverse=True)
stats_dict['sourcedest']['list'].sort(reverse=True)
stats_dict['conversation']['list'].sort(reverse=True)
    
json_string = json.dumps(stats_dict, indent=2)
with open(output_stats_path, 'w') as outfile:
    outfile.write(json_string)

print (i)
print (stats)
# print (stats_dict)
