#!/bin/bash
cd /opt/tt-ran/tt/cmake_targets/ran_build/build/
./nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod --TAP 1 --TTI 1 --SNR 1