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
        ping_output=f.read()
    match = re.search(r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms", ping_output)

    return match


def processDATA():
   

    # ul_snr_values_a = []
    # ul_mcs_values_a = []
    # dl_mcs_values_a = []
    # ul_tpt_values_a = []
    # dl_tpt_values_a = []
    # ul_cqi_values_a = []

    # ul_snr_ttis_a = []
    # ul_mcs_ttis_a = []
    # dl_mcs_ttis_a = []
    # ul_tpt_ttis_a = []
    # dl_tpt_ttis_a = []
    # ul_cqi_ttis_a = []
    exp_list=[]
    for kk in [1,5,9,13,17,20]:
        print(f"UE{kk}")
        # read from TTI file
        ### @ALI: change this to whatever file you would like to point
        exp_list_in=[]
        for i in range(1,6):
            match = read_starting(f"./plot/ue5_{kk}/dl_ue{i}.txt")
            exp_list_in.append(match.group(1))
            print(match)
        exp_list.append(exp_list_in)
    print (exp_list)
        

    data = exp_list
    x = []
    y = []
    variance = []

    for sublist in data:
        x.append(len(sublist))
        numeric_values = [float(value) for value in sublist]
        average = np.mean(numeric_values)
        y.append(average)
        variance.append(np.sqrt(np.var(numeric_values)))

    # Create the plot
    plt.errorbar([1,5,9,13,17,20], y, yerr=variance, fmt='o-', capsize=5)  # Use errorbar for variance bars
    plt.xlabel("Number of Taps")
    plt.ylabel("Average Ping RTT")
    plt.title("Average Ping RTT vs. Number of Taps")
    plt.grid(True)
      
       

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
    plt.savefig(f"plotting_tti_ue_tap1.png")

       

if __name__ == "__main__":
    

    processDATA()

    print("Done!")