#!/bin/sh


#python generator.py -i ../datasets/kitsune/Mirai_pcap.pcap.tsv -o ../datasets/kitsune/Mirai.csv


CMD_IN="python generator.py -i ../datasets/kitsune/"
CMD_OUT="-o ../datasets/kitsune/"
PCAP="_pcap.pcap.tsv"
PCAPNG="_pcap.pcapng.tsv"
CSV=".csv"

WTAP="Active_Wiretap"
ARP="ARP_MitM"
FUZZ="Fuzzing"
MIRAI="Mirai"
SSDP="SSDP_Flood"

tmux new-session -d -s "gnrtr" -n "WTAP" bash -c "$CMD_IN$WTAP$PCAPNG $CMD_OUT$WTAP$CSV"
tmux new-window -t "gnrtr" -n "ARP" bash -c "$CMD_IN$ARP$PCAPNG $CMD_OUT$ARP$CSV"
tmux new-window -t "gnrtr" -n "FUZZ" bash -c "$CMD_IN$FUZZ$PCAPNG $CMD_OUT$FUZZ$CSV"
tmux new-window -t "gnrtr" -n "MIRAI" bash -c "$CMD_IN$MIRAI$PCAP $CMD_OUT$MIRAI$CSV"
tmux new-window -t "gnrtr" -n "SSDP" bash -c "$CMD_IN$SSDP$PCAP $CMD_OUT$SSDP$CSV"

