#!/bin/sh


#python switch_dataset_generator.py -i ../datasets/kitsune/Mirai_pcap.pcap.tsv -o ../datasets/kitsune/Mirai_switch_100.csv -n 33324


CMD_IN="python switch_dataset_generator.py -i ../datasets/kitsune/"
CMD_OUT="-o ../datasets/kitsune/"
PCAP="_pcap.pcap.tsv"
PCAPNG="_pcap.pcapng.tsv"
SWITCH="_switch_"
CSV=".csv"

WTAP="Active_Wiretap"
ARP="ARP_MitM"
FUZZ="Fuzzing"
MIRAI="Mirai"
SSDP="SSDP_Flood"

P100="100"
# WTAP100=" -n 299"
# ARP100=" -n 1133"
# FUZZ100=" -n 3666"
# MIRAI100=" -n 104604"
# SSDP100=" -n 131711"
WTAP100=" -n 29900"
ARP100=" -n 113300"
FUZZ100=" -n 366600"
MIRAI100=" -n 10460400"
SSDP100=" -n 13171100"

P50="50"
WTAP50=" -n 150"
ARP50=" -n 567"
FUZZ50=" -n 1833"
MIRAI50=" -n 52302"
SSDP50=" -n 65856"

P25="25"
WTAP25=" -n 75"
ARP25=" -n 283"
FUZZ25=" -n 917"
MIRAI25=" -n 26151"
SSDP25=" -n 32928"

P10="10"
WTAP10=" -n 30"
ARP10=" -n 113"
FUZZ10=" -n 367"
MIRAI10=" -n 10460"
SSDP10=" -n 13171"

P5="5"
WTAP5=" -n 15"
ARP5=" -n 57"
FUZZ5=" -n 183"
MIRAI5=" -n 5230"
SSDP5=" -n 6586"

P1="1"
WTAP1=" -n 3"
ARP1=" -n 11"
FUZZ1=" -n 37"
MIRAI1=" -n 1046"
SSDP1=" -n 1317"


# tmux new-session -d -s "gnrtr" -n "WTAP100" bash -c "$CMD_IN$WTAP$PCAPNG $CMD_OUT$WTAP$SWITCH$P100$CSV $WTAP100"
tmux new-session -d -s "gnrtr" -n WTAP50 bash -c "$CMD_IN$WTAP$PCAPNG $CMD_OUT$WTAP$SWITCH$P50$CSV $WTAP50"
tmux new-window -t "gnrtr" -n WTAP25 bash -c "$CMD_IN$WTAP$PCAPNG $CMD_OUT$WTAP$SWITCH$P25$CSV $WTAP25"
tmux new-window -t "gnrtr" -n WTAP10 bash -c "$CMD_IN$WTAP$PCAPNG $CMD_OUT$WTAP$SWITCH$P10$CSV $WTAP10"
tmux new-window -t "gnrtr" -n WTAP5 bash -c "$CMD_IN$WTAP$PCAPNG $CMD_OUT$WTAP$SWITCH$P5$CSV $WTAP5"
tmux new-window -t "gnrtr" -n WTAP1 bash -c "$CMD_IN$WTAP$PCAPNG $CMD_OUT$WTAP$SWITCH$P1$CSV $WTAP1"

# tmux new-window -t "gnrtr" -n "ARP100" bash -c "$CMD_IN$ARP$PCAPNG $CMD_OUT$ARP$SWITCH$P100$CSV $ARP100"
tmux new-window -t "gnrtr" -n ARP50 bash -c "$CMD_IN$ARP$PCAPNG $CMD_OUT$ARP$SWITCH$P50$CSV $ARP50"
tmux new-window -t "gnrtr" -n ARP25 bash -c "$CMD_IN$ARP$PCAPNG $CMD_OUT$ARP$SWITCH$P25$CSV $ARP25"
tmux new-window -t "gnrtr" -n ARP10 bash -c "$CMD_IN$ARP$PCAPNG $CMD_OUT$ARP$SWITCH$P10$CSV $ARP10"
tmux new-window -t "gnrtr" -n ARP5 bash -c "$CMD_IN$ARP$PCAPNG $CMD_OUT$ARP$SWITCH$P5$CSV $ARP5"
tmux new-window -t "gnrtr" -n ARP1 bash -c "$CMD_IN$ARP$PCAPNG $CMD_OUT$ARP$SWITCH$P1$CSV $ARP1"

# tmux new-window -t "gnrtr" -n "FUZZ100" bash -c "$CMD_IN$FUZZ$PCAPNG $CMD_OUT$FUZZ$SWITCH$P100$CSV $FUZZ100"
tmux new-window -t "gnrtr" -n FUZZ50 bash -c "$CMD_IN$FUZZ$PCAPNG $CMD_OUT$FUZZ$SWITCH$P50$CSV $FUZZ50"
tmux new-window -t "gnrtr" -n FUZZ25 bash -c "$CMD_IN$FUZZ$PCAPNG $CMD_OUT$FUZZ$SWITCH$P25$CSV $FUZZ25"
tmux new-window -t "gnrtr" -n FUZZ10 bash -c "$CMD_IN$FUZZ$PCAPNG $CMD_OUT$FUZZ$SWITCH$P10$CSV $FUZZ10"
tmux new-window -t "gnrtr" -n FUZZ5 bash -c "$CMD_IN$FUZZ$PCAPNG $CMD_OUT$FUZZ$SWITCH$P5$CSV $FUZZ5"
tmux new-window -t "gnrtr" -n FUZZ1 bash -c "$CMD_IN$FUZZ$PCAPNG $CMD_OUT$FUZZ$SWITCH$P1$CSV $FUZZ1"

# tmux new-window -t "gnrtr" -n "MIRAI100" bash -c "$CMD_IN$MIRAI$PCAP $CMD_OUT$MIRAI$SWITCH$P100$CSV $MIRAI100"
tmux new-window -t "gnrtr" -n MIRAI50 bash -c "$CMD_IN$MIRAI$PCAP $CMD_OUT$MIRAI$SWITCH$P50$CSV $MIRAI50"
tmux new-window -t "gnrtr" -n MIRAI25 bash -c "$CMD_IN$MIRAI$PCAP $CMD_OUT$MIRAI$SWITCH$P25$CSV $MIRAI25"
tmux new-window -t "gnrtr" -n MIRAI10 bash -c "$CMD_IN$MIRAI$PCAP $CMD_OUT$MIRAI$SWITCH$P10$CSV $MIRAI10"
tmux new-window -t "gnrtr" -n MIRAI5 bash -c "$CMD_IN$MIRAI$PCAP $CMD_OUT$MIRAI$SWITCH$P5$CSV $MIRAI5"
tmux new-window -t "gnrtr" -n MIRAI1 bash -c "$CMD_IN$MIRAI$PCAP $CMD_OUT$MIRAI$SWITCH$P1$CSV $MIRAI1"

# tmux new-window -t "gnrtr" -n "SSDP100" bash -c "$CMD_IN$SSDP$PCAP $CMD_OUT$SSDP$SWITCH$P100$CSV $SSDP100"
tmux new-window -t "gnrtr" -n SSDP50 bash -c "$CMD_IN$SSDP$PCAP $CMD_OUT$SSDP$SWITCH$P50$CSV $SSDP50"
tmux new-window -t "gnrtr" -n SSDP25 bash -c "$CMD_IN$SSDP$PCAP $CMD_OUT$SSDP$SWITCH$P25$CSV $SSDP25"
tmux new-window -t "gnrtr" -n SSDP10 bash -c "$CMD_IN$SSDP$PCAP $CMD_OUT$SSDP$SWITCH$P10$CSV $SSDP10"
tmux new-window -t "gnrtr" -n SSDP5 bash -c "$CMD_IN$SSDP$PCAP $CMD_OUT$SSDP$SWITCH$P5$CSV $SSDP5"
tmux new-window -t "gnrtr" -n SSDP1 bash -c "$CMD_IN$SSDP$PCAP $CMD_OUT$SSDP$SWITCH$P1$CSV $SSDP1"

