#!/bin/bash
cd /opt/tt-ran/tt/cmake_targets/ran_build/build/
<<<<<<< HEAD
#./nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --TAP 1 --TTI 1 --SNR 1 --MCS 1 --CQI 1 --TPT 1 >gnb.log &
./nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa --rfsimulator.options chanmod --TAP 1 --TTI 1  >gnb.log &
=======
./nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod --TAP 1 --TTI 1 --SNR 1 --MCS 1 --CQI 1 --TPT 1 &
>>>>>>> 1de0aa1fabc135914cd0959f8bd3be02123199ae
pid=$!
echo $pid > pid.txt