#!/bin/bash

# new tmux session
tmux new-session -d -s session1

# create 4 windows
tmux split-window -h
tmux split-window -v
# tmux select-pane -R
# tmux split-window -v

## UL
# Send the first command to the first pane --> setup the UL server on the ext-dn
tmux send-keys -t session1:0.0 "docker exec -it oai-ext-dn iperf -s -i 1 -B 192.168.71.135" C-m

# Send the second command to the second pane --> transmit data from the UE containers
tmux send-keys -t session1:0.1 "docker exec -it tt-nrue151 bash" C-m
# save IP address of the UE container from terminal
tmux send-keys -t session1:0.1 "net_address=$(ifconfig oaitun| grep 'inet ' | awk '{print $2}') " C-m
tmux send-keys -t session1:0.1 "iperf -t 86400 -i 1 -fk -c 192.168.71.135 -b 2M -B $net_address" C-m

## DL
# # send command to the third pane --> setup the DL server on the UE container
 tmux send-keys -t session1:0.2 "docker exec -it tt-nrue1 iperf -s -u -i 1 -B $net_address" C-m

# send command to the fourth pane
tmux send-keys -t session1:0.3 "docker exec -it oai-ext-dn iperf -u -t 86400 -i 1 -fk -B 192.168.71.135 -b 2M -c $net_address" C-m

# Attach to the tmux session
tmux attach-session -t session1