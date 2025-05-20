import sys
import os
import time
import threading
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 

def read_starting(file_name):
    float_values = []
    with open(file_name, 'r') as f:
        for i, line in enumerate(f, start=1):
            # if (i-1) % 3 == 0:
            words = line.split()
            if len(words) >= 1:
                try:
                    float_value = float(words[0])  # Convert the 4th word to float
                    float_values.append(float_value)
                except ValueError:
                    print(f"Cannot convert '{words[0]}' to float on line {i}")
            else:
                print(f"Line {i} does not have 4 words")
    return float_values


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

    plt.figure(figsize=(6, 4))

# Tap configurations to evaluate
    tap_configs = [0,1, 5, 9, 13, 17, 20, 50, 100]  # i.e., 1, 5, 9, 13, 17

    for kk in tap_configs:
        filepath = f"./plot/ue5_{kk}/tti.txt"
        
        if not os.path.exists(filepath):
            print(f"[Warning] File not found: {filepath}")
            continue

        vals_tti = read_starting(filepath)

        # Compute TTI differences in seconds
        diff_tti = [(vals_tti[i] - vals_tti[i - 1]) / 1e9 for i in range(1, len(vals_tti))]
        
        # Remove zeros and negative values
        tti = [max(0, val) for val in diff_tti if val > 0]
        
        if not tti:
            print(f"[Info] No valid TTI values in: {filepath}")
            continue

        # Keep last 4000 samples
        size = 7000
        tti = tti[-size:] if len(tti) > size else tti

        # Compute CCDF
        sorted_tti = np.sort(tti)
        p1 = np.linspace(0, 1, len(sorted_tti))
        ccdf = 1 - p1

        # Plot line
        plt.plot(sorted_tti, ccdf, label=f'{kk} Tap(s)', linewidth=3)

    # Add 3GPP TTI threshold line (1 ms)
    plt.axvline(x=0.001, color='red', linestyle='--', linewidth=3, label='3GPP TTI = 1 ms')

    # Plot formatting
    # plt.xlabel('TTI Times (s)', fontsize=14)
    # plt.ylabel('$CCDF$', fontsize=14)
    # plt.title('TTI Variation With Number Of Taps (CCDF)', fontsize=16)
    plt.xlim(0, 0.01)
    plt.xticks(fontsize=14, rotation=45)
    plt.yticks(fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.7, color='gray')
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':', linewidth=0.5, color='lightgray')
    plt.legend()
    plt.tight_layout()

    # Save and show
    plt.savefig("tti_variation_ccdf_all_taps_opt2_with0.pdf", format="png", dpi=150)

       

if __name__ == "__main__":
    

    processDATA()

    print("Done!")