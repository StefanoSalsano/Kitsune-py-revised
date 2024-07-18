from Kitsune import Kitsune
import numpy as np
import time
import sys


##############################################################################
# Kitsune a lightweight online network intrusion detection system based on an ensemble of autoencoders (kitNET).
# For more information and citation, please see our NDSS'18 paper: Kitsune: An Ensemble of Autoencoders for Online Network Intrusion Detection

# This script demonstrates Kitsune's ability to incrementally learn, and detect anomalies in recorded a pcap of the Mirai Malware.
# The demo involves an m-by-n dataset with n=115 dimensions (features), and m=100,000 observations.
# Each observation is a snapshot of the network's state in terms of incremental damped statistics (see the NDSS paper for more details)

#The runtimes presented in the paper, are based on the C++ implimentation (roughly 100x faster than the python implimentation)
###################  Last Tested with Anaconda 3.6.3   #######################

# Load Mirai pcap (a recording of the Mirai botnet malware being activated)
# The first 70,000 observations are clean...
#print("Unzipping Sample Capture...")
#import zipfile
#with zipfile.ZipFile("mirai.zip","r") as zip_ref:
#    zip_ref.extractall()


# File location
#path = "mirai.pcap" #the pcap, pcapng, or tsv file to process.
#path = "mirai2000.pcap" #the pcap, pcapng, or tsv file to process.
#path = "Mirai_pcap.pcap" #the pcap, pcapng, or tsv file to process.
path = "Mirai_pcap.pcap.tsv" #the pcap, pcapng, or tsv file to process.



packet_limit = np.Inf #the number of packets to process
packet_limit = 100000 #the number of packets to process
packet_limit = 1000

# KitNET params:
maxAE = 10 #maximum size for any autoencoder in the ensemble layer
FMgrace = 5000 #the number of instances taken to learn the feature mapping (the ensemble's architecture)
FMgrace = np.Inf
ADgrace = 50000 #the number of instances used to train the anomaly detector (ensemble itself)
ADgrace = np.Inf

# Build Kitsune
K = Kitsune(path,packet_limit,maxAE,FMgrace,ADgrace)

print("Running Kitsune:")

collector = []
RMSEs = []
i = 0
start = time.time()
# Here we process (train/execute) each individual packet.
# In this way, each observation is discarded after performing process() method.
while True:
    i+=1
    if i % 1000 == 0:
        print(i)
    rmse = K.proc_next_packet(collector)
    if rmse == -1:
        break
    RMSEs.append(rmse)
stop = time.time()

#analysis of flow statistics
#K.FE.evaluate_stats()

#useful for debug
#saves into json_data.json time values series for all flows (H and Hp)
#K.FE.export_flow_time_values() 

print("Complete ok. Time elapsed: "+ str(stop - start))

#sys.exit()

import pandas as pd
df = pd.DataFrame(collector)

converter=dict()
row_converter=dict()
for i in range(0,115) :
    converter[i]=i+1
for i in range(0,len(df)) :
    row_converter[i]=i+1
df.rename (columns=converter,index=row_converter,inplace=True)
rows_to_read=1000
miraidf = pd.read_csv('Mirai_dataset.csv', header=None, index_col=0, nrows=rows_to_read)
#miraidf = pd.read_csv('Mirai_dataset.csv', header=None, index_col=0, nrows=100000)
for i in range(0,rows_to_read-1):
  for j in range(1,116):
    error = abs(df.at[i+1,j]-miraidf.at[i,j])
    if error > 1e-7 :
        if (error / miraidf.at[i,j]) > 1e-7 :
            if abs (miraidf.at[i,j]/df.at[i+1,j]-2) > 1e-3 :
                indice=(j-36) % 7
                if not ((indice==0 or indice==1) and j>35 and j < 66) :
                    print(i+1,j,df.at[i+1,j]-miraidf.at[i,j],df.at[i+1,j],miraidf.at[i,j])


#print (df)
df.to_csv('output.csv')

sys.exit()

# Here we demonstrate how one can fit the RMSE scores to a log-normal distribution (useful for finding/setting a cutoff threshold \phi)
from scipy.stats import norm
benignSample = np.log(RMSEs[FMgrace+ADgrace+1:100000])
logProbs = norm.logsf(np.log(RMSEs), np.mean(benignSample), np.std(benignSample))

# plot the RMSE anomaly scores
print("Plotting results")
from matplotlib import pyplot as plt
from matplotlib import cm
plt.figure(figsize=(10,5))
fig = plt.scatter(range(FMgrace+ADgrace+1,len(RMSEs)),RMSEs[FMgrace+ADgrace+1:],s=0.1,c=logProbs[FMgrace+ADgrace+1:],cmap='RdYlGn')
plt.yscale("log")
plt.title("Anomaly Scores from Kitsune's Execution Phase")
plt.ylabel("RMSE (log scaled)")
plt.xlabel("Time elapsed [min]")
figbar=plt.colorbar()
figbar.ax.set_ylabel('Log Probability\n ', rotation=270)
plt.show()