#!/bin/bash
pid=$(cat /opt/tt-ran/tt/cmake_targets/ran_build/build/pid.txt)
kill $pid