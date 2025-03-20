#!/bin/bash

# Start a new tmux session
tmux new-session -d -s session1

# Split the window horizontally
tmux split-window -h

# Send the first command to the first pane
tmux send-keys -t session1:0.0 "docker exec -it tt-nrue1 bash" C-m


# Send the second command to the second pane
tmux send-keys -t session1:0.1 "docker exec -it oai-ext-dn iperf -u -t 86400 -i 1 -fk -B 192.168.70.135 -b 20M -c 10.0.0.8" C-m

# Attach to the tmux session
tmux attach-session -t session1