#!/bin/bash
cd /opt/tt-ran/tt/cmake_targets
./build_oai --gNB --nrUE
pid=$!
echo $pid > pid.txt