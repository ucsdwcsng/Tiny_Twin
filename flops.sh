#!/bin/bash
# Run perf stat and calculate FLOPS

perf_output=$(perf stat -e r5301c7,r5302c7,r5304c7,r5308c7,r5310c7,r5320c7,r5340c7,r5380c7 2>&1)
events=$(echo "$perf_output" | awk '/r530/{sum += $1} END {print sum}')
time_elapsed=$(echo "$perf_output" | awk '/seconds time elapsed/ {print $1}')

echo "Total Floating Point Operations: $events"
echo "Time Elapsed: $time_elapsed seconds"
flops=$(echo "scale=2; $events / $time_elapsed" | bc)
echo "FLOPS: $flops"

