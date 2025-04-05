from collections import defaultdict
import sys
import os
import time
import threading
import numpy as np
import matplotlib
import re
matplotlib.use('Agg')
import matplotlib.pyplot as plt 

def read_starting(file_name):
    float_values = []
    with open(file_name, 'r') as f:
        top_output=f.read()
    nr_lines = [line for line in top_output.splitlines() if "nr-" in line]

    return nr_lines


def processDATA():
   

    exp_list=[]
    for kk in [1,5,9,13,17, 20]:
        print(f"Tap{kk}")
        # read from TTI file
        ### @ALI: change this to whatever file you would like to point
        exp_list_in=[]
        
        match = read_starting(f"./plot/ue5_{kk}/iperf_cpumem.txt")
        exp_list.append(match)
            
    print(exp_list)



    cpu_usage_by_pid = defaultdict(list)

    # Split lines and group CPU usage (9th element) by PID (1st element)
    for data in exp_list:
        print("__________________")
        cpu_by_pid = defaultdict(list)
        mem_by_pid = defaultdict(list)
        for line in data:
            parts = line.split()
            pid = parts[0]
            cpu = parts[8]
            mem = parts[9]
            try:
                cpu_by_pid[pid].append(float(cpu))
                mem_by_pid[pid].append(float(mem))
            except ValueError:
                continue  # Skip any lines with unexpected formatting

        # Calculate mean CPU usage for each PID
       

        
        

# Calculate mean CPU and MEM usage for each PID
        summary = {
            pid: {
                "mean_cpu": sum(cpu_by_pid[pid]) / len(cpu_by_pid[pid]),
                "mean_mem": sum(mem_by_pid[pid]) / len(mem_by_pid[pid]),
            }
            for pid in cpu_by_pid
        }

        # Optional: print results
        for pid, stats in sorted(summary.items()):
            print(f"PID: {pid}, Mean %CPU: {stats['mean_cpu']:.2f}, Mean %MEM: {stats['mean_mem']:.2f}")
    
    # print (exp_list)
            

    # data = exp_list
    # x = []
    # y = []
    # variance = []

    # for sublist in data:
    #     x.append(len(sublist))
    #     numeric_values = [float(value) for value in sublist]
    #     average = np.mean(numeric_values)
    #     y.append(average)
    #     variance.append(np.sqrt(np.var(numeric_values)))

    # # Create the plot
    # plt.errorbar([1,5,9,13,17,20], y, yerr=variance, fmt='o-', capsize=5)  # Use errorbar for variance bars
    # plt.xlabel("Number of Taps")
    # plt.ylabel("Average Ping RTT")
    # plt.title("Average Ping RTT vs. Number of Taps")
    # plt.grid(True)
      
       

    # 8 subplots
    # fig, axes = plt.subplots(1, 1, figsize=(20, 10), dpi=150)

    # plot CCDF
    # ax1 = axes[0, 0]
    # ax1.plot(sorted_tti, 1 - p1, label='1 Tap', linewidth=2)

    # # add a red vertical line at x=0.001 --> 3GPP TTI timing
    # ax1.axvline(x=0.001, color='red', linestyle='--', linewidth=2)

    # ax1.set_xlabel('TTI Times (s)', fontsize=14)
    # ax1.set_ylabel('$CCDF$', fontsize=14)
    # ax1.set_title('TTI Variation With Number Of Taps (CCDF)', fontsize=16)

    # # Set x-axis limit
    # ax1.set_xlim(0, 0.01)

    # # Customize the grid
    # ax1.grid(True, which='both', linestyle='--', linewidth=0.7, color='gray')

    # # Add minor ticks for a finer grid
    # ax1.minorticks_on()
    # ax1.grid(which='minor', linestyle=':', linewidth=0.5, color='lightgray')

    # ax1.legend()  # Add legend

    # fig.savefig(f"plotting_tti_ue{kk}_1.png", format="png", dpi=150)
    # plt.savefig(f"plotting_tti_ue_tap1.png")

       

if __name__ == "__main__":
    

    processDATA()

    print("Done!")