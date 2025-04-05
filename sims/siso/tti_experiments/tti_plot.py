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

    for kk in range(1,20,4):

   
        # read from TTI file
        ### @ALI: change this to whatever file you would like to point
        vals_tti = read_starting(f"./plot/ue5_{kk}/tti.txt")
        diff_tti = [vals_tti[i] - vals_tti[i - 1] for i in range(1, len(vals_tti))]
        diff_tti = [diff_tti[i]/1000000000 for i in range(1, len(diff_tti))]

        tti = np.array(diff_tti)
        tti = [max(0, tti_val) for tti_val in tti]
        # remove all zero values
        tti = [tti_val for tti_val in tti if tti_val > 0]
        mean_tti = np.mean(tti)

        size = 4000

        # CCDFs of various TTI times across 100,000 instances
        tti = tti[len(tti)-size:len(tti)]
        sorted_tti = np.sort(tti)
        p1 = np.linspace(0, 1, len(tti))

        # 8 subplots
        fig, axes = plt.subplots(2, 4, figsize=(20, 10), dpi=150)

        # plot CCDF
        ax1 = axes[0, 0]
        ax1.plot(sorted_tti, 1 - p1, label='1 Tap', linewidth=2)

        # add a red vertical line at x=0.001 --> 3GPP TTI timing
        ax1.axvline(x=0.001, color='red', linestyle='--', linewidth=2)

        ax1.set_xlabel('TTI Times (s)', fontsize=14)
        ax1.set_ylabel('$CCDF$', fontsize=14)
        ax1.set_title('TTI Variation With Number Of Taps (CCDF)', fontsize=16)

        # Set x-axis limit
        ax1.set_xlim(0, 0.01)

        # Customize the grid
        ax1.grid(True, which='both', linestyle='--', linewidth=0.7, color='gray')

        # Add minor ticks for a finer grid
        ax1.minorticks_on()
        ax1.grid(which='minor', linestyle=':', linewidth=0.5, color='lightgray')

        ax1.legend()  # Add legend

        plt.savefig("tti_variation_ccdf.png", format="png", dpi=150)

        ### read MAC metrics
        # define all_vals

        # ul_snr_values = []
        # ul_mcs_values = []
        # dl_mcs_values = []
        # ul_tpt_values = []
        # dl_tpt_values = []
        # ul_cqi_values = []

        # ul_snr_ttis = []
        # ul_mcs_ttis = []
        # dl_mcs_ttis = []
        # ul_tpt_ttis = []
        # dl_tpt_ttis = []
        # ul_cqi_ttis = []

        
        # # ul_cumulative = []
        # # dl_cumulative = []
        # # for rnti in all_vals.keys():
        # #     # Assuming tpt_ttis and tpt_values are already defined
        # #     ul_tpt = Convert(all_vals[rnti]['ul_tpt_ttis'], all_vals[rnti]['ul_tpt_values'])
        # #     dl_tpt = Convert(all_vals[rnti]['dl_tpt_ttis'], all_vals[rnti]['dl_tpt_values'])

        # WINDOW_SIZE = 1000
        # cumulative_tpt = 0

        # # Iterate through the keys of tpt
        # for key in ul_tpt:
        #     for rnti in 
        #     cumulative_tpt += ul_tpt[key]
        #     if key % WINDOW_SIZE == 0:
        #         cumulative_ul_tpt_values.append(cumulative_tpt)
        #         cumulative_tpt = 0

        #     cumulative_tpt = 0

        #     # Iterate through the keys of tpt
        #     for key in dl_tpt:
        #         cumulative_tpt += dl_tpt[key]
        #         if key % WINDOW_SIZE == 0:
        #             cumulative_dl_tpt_values.append(cumulative_tpt)
        #             cumulative_tpt = 0   




        # # Plotting the cumulative TPT values
        # ax3.plot(ul, label='UL TPT')
        # ax3.plot(dl, label='DL TPT')

        # # Adding labels and title
        # ax3.set_xlabel('(TTI) Index')
        # ax3.set_ylabel('TPT')
        # ax3.set_title('UL and DL Traffic at capacity')

        # # Adding legend
        # ax3.legend()

        # plotting on the fourth plot
        
        # Plotting the cumulative CQI values
        

        # Plotting the cumulative SNR values
        

        fig.savefig(f"plottingue5_{kk}.png", format="png", dpi=150)

       

if __name__ == "__main__":
    

    processDATA()

    print("Done!")