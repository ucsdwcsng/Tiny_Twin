import sys
import os
import time
import threading
import numpy as np
import matplotlib.pyplot as plt 

start='''
services:
    tt-gnb:
        image: tt-gnb:v2
        container_name: tt-gnb
        privileged: true
        cap_drop:
            - ALL
        cap_add:
            - NET_ADMIN  # for interface bringup
            - NET_RAW    # for ping
        volumes:
            - ../../../../tinytwin-oai:/opt/tt-ran/tt:rw
            - ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf:/opt/tt-ran/etc/gnb.conf
            - ../../../channel/channel.txt:/opt/tt-ran/tt/channel/channel_gradual.txt
            - ../../../logs_gnb:/opt/tt-ran/etc/logs
            - ./run.sh:/opt/tt-ran/run.sh
        # environment:
        #     USE_ADDITIONAL_OPTIONS: --rfsim -E --sa --rfsimulator.options chanmod -T 10 -O /opt/oai-gnb/etc/gnb.conf
        #     ASAN_OPTIONS: detect_leaks=0
        # entrypoint: >
        #     /bin/bash -c "pwd && cd tt/cmake_targets/ran_build/build/ &&
        #     ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod -TP 10 --TTI 1 --SNR 1
        #     exec /bin/bash"
        entrypoint: /bin/bash
        stdin_open: true  # docker run -i
        tty: true        # docker run -t
        # depends_on:
        #     - oai-ext-dn
        networks:
            public_net:
                ipv4_address: 192.168.70.140
        # healthcheck:
        #     test: /bin/bash -c "pgrep nr-softmodem"
        #     interval: 10s
        #     timeout: 5s
        #     retries: 5

'''
end='''

networks:
    public_net:
        driver: bridge
        external: true
        name: tt-public-net
'''

flag=1

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

def read_exec(file_name):
    float_values = []
    with open(file_name, 'r') as f:
        for i, line in enumerate(f, start=1):
            if i % 3 == 0:
                words = line.split()
                if len(words) >= 4:
                    try:
                        float_value = float(words[2])  # Convert the 4th word to float
                        float_values.append(float_value)
                    except ValueError:
                        print(f"Cannot convert '{words[3]}' to float on line {i}")
                else:
                    print(f"Line {i} does not have 4 words")
    return float_values    

def read_more(file_name):
    ul_snr_values = []
    ul_mcs_values = []
    dl_mcs_values = []
    ul_tpt_values = []
    dl_tpt_values = []
    ul_cqi_values = []

    ul_snr_ttis = []
    ul_mcs_ttis = []
    dl_mcs_ttis = []
    ul_tpt_ttis = []
    dl_tpt_ttis = []
    ul_cqi_ttis = []

    previous_line = None

    with open(file_name, 'r') as f:
        for i, line in enumerate(f, start=1):
            # if (i-1) % 2 == 0:
            words = line.split()
            if len(words) >= 1:
                try:
                    float_value = float(words[2])  # Convert the last word to float
                    if words[0] == 'UL':
                        # extra = float(words[3])
                        if words[1] == 'SNR:':
                            # refer to previous line
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                ul_snr_ttis.append(tti)
                            ul_snr_values.append(float_value)
                        elif words[1] == 'MCS:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                ul_mcs_ttis.append(tti)
                            ul_mcs_values.append(float_value)
                        elif words[1] == 'TPT:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                ul_tpt_ttis.append(tti)
                            ul_tpt_values.append(float_value)
                        elif words[1] == 'CQI:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                ul_cqi_ttis.append(tti)
                            ul_cqi_values.append(float_value)
                    elif words[0] == 'DL':
                        if words[1] == 'MCS:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                ul_mcs_ttis.append(tti)
                            ul_mcs_values.append(float_value)

                except ValueError:
                    print(f"Cannot convert '{words[2]}' to float on line {i}")
            else:
                print(f"Line {i} does not have 4 words")
            previous_line = line
    return ul_snr_values, ul_snr_values, ul_cqi_values, ul_cqi_ttis, ul_mcs_values, ul_mcs_ttis, dl_mcs_values, dl_mcs_ttis, ul_tpt_values, ul_tpt_ttis, dl_tpt_values, dl_tpt_ttis

def Convert(snr_ttis, snr_values):
    res_dct = {snr_ttis[i]: snr_values[i] for i in range(len(snr_ttis))}
    return res_dct

def create_docker(i):
    template=f'''
    tt-nrue{i}:
        image: tt-nrue:v2
        container_name: tt-ue{i}
        privileged: true
        cap_drop:
            - ALL
        cap_add:
            - NET_ADMIN  # for interface bringup
            - NET_RAW    # for ping
        volumes:
            - ../../../../tinytwin-oai:/opt/tt-ran/tt:rw   
            # - ../../../channel/channel.txt:/opt/tt-ran/channel/channel_gradual.txt
            - ../../../ci-scripts/conf_files/nrue.uicc.conf:/opt/oai-nr-ue/etc/nr-ue.conf
            - ../../../logs_ue:/opt/oai-nr-ue/etc/logs
        entrypoint: >
            /bin/bash -c "ls && cd tt/cmake_targets/ran_build/build/ &&
            ./nr-uesoftmodem --uicc0.imsi 00101000000000{i-150} -C 3619200000 -r 106 --numerology 1 --ssb 516 -E --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf --TAP {sys.argv[2]} --rfsimulator.serveraddr 192.168.70.140 &&
            exec /bin/bash"
        # entrypoint: /bin/bash
        stdin_open: true  
        tty: true        
        networks:
            public_net:
                ipv4_address: 192.168.70.{i}
        devices:
             - /dev/net/tun:/dev/net/tun
        healthcheck:
            test: /bin/bash -c "pgrep nr-uesoftmodem"
            interval: 10s
            timeout: 5s
            retries: 5
 
    '''
    return template

def autoUE():
    global flag
    flag=1
    for kk in range(1,int(sys.argv[1])+1):
        
        while flag == 0:
            time.sleep(2)
        

        file=""
        for i in range(151,151+kk):
            file=file+"\n"+create_docker(i)
        file = start+ file+ end
        print(file)

        
        with open("./docker-compose.yaml","+w") as f:
            f.write(file)
        os.system(f"docker compose up -d tt-gnb")
        print("set up ran")
        time.sleep(15)
        os.system(f"docker exec -it tt-gnb chmod +x run.sh ")
        #os.system(f"docker exec -d tt-gnb ./run.sh ")
        #os.system(f"docker exec -d tt-gnb  cd /opt/tt-ran/tt/cmake_targets/ran_build/build/ && ./nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod --TAP 1 --TTI 1 --SNR 1")
        for i in range(151,151+kk):
            os.system(f"docker compose up -d tt-nrue{i}")
            time.sleep(min((i-150)*6,37))
        time.sleep(120)
        print("kill gnb")
        time.sleep(15)

        os.system(f"docker compose down")

        flag=0

def processDATA():
    global flag
    time.sleep(2)

    for kk in range(1,int(sys.argv[1])+1):
        flag=1
        while flag == 1:
            time.sleep(2)

        # read from TTI file
        ### @ALI: change this to whatever file you would like to point
        vals_tti = read_starting("../../../logs/tti.txt")
        diff_tti = [vals_tti[i] - vals_tti[i - 1] for i in range(1, len(vals_tti))]
        diff_tti = [diff_tti[i]/1000000000 for i in range(1, len(diff_tti))]

        tti = np.array(diff_tti)
        tti = [max(0, tti_val) for tti_val in tti]
        # remove all zero values
        tti = [tti_val for tti_val in tti if tti_val > 0]
        mean_tti = np.mean(tti)

        size = 100000

        # CCDFs of various TTI times across 100,000 instances
        tti = tti[:size]
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
        ul_snr_values = []
        ul_mcs_values = []
        dl_mcs_values = []
        ul_tpt_values = []
        dl_tpt_values = []
        ul_cqi_values = []

        ul_snr_ttis = []
        ul_mcs_ttis = []
        dl_mcs_ttis = []
        ul_tpt_ttis = []
        dl_tpt_ttis = []
        ul_cqi_ttis = []

        ul_snr_values, ul_snr_values, ul_cqi_values, ul_cqi_ttis, ul_mcs_values, ul_mcs_ttis, dl_mcs_values, dl_mcs_ttis, ul_tpt_values, ul_tpt_ttis, dl_tpt_values, dl_tpt_ttis = read_more()

        # Plot on the second subplot (0, 1)
        ax2 = axes[0, 1]

        ax2.plot(ul_mcs_values, label='UL MCS')
        ax2.plot(dl_mcs_values, label='DL MCS')

        # Adding labels and title
        ax2.set_xlabel('(TTI) Index')
        ax2.set_ylabel('MCS')
        ax2.set_title('MCS Variation')

        # Adding legend
        ax2.legend()

        # Displaying the plot
        plt.tight_layout()
        # plt.show()

        # Plot on the third subplot (0, 2)
        ax3 = axes[0, 2]

        # Assuming tpt_ttis and tpt_values are already defined
        ul_tpt = Convert(ul_tpt_ttis, ul_tpt_values)
        dl_tpt = Convert(dl_tpt_ttis, dl_tpt_values)

        WINDOW_SIZE = 1000
        cumulative_tpt = 0
        cumulative_ul_tpt_values = []

        # Iterate through the keys of tpt
        for key in ul_tpt:
            cumulative_tpt += ul_tpt[key]
            if key % WINDOW_SIZE == 0:
                cumulative_ul_tpt_values.append(cumulative_tpt)
                cumulative_tpt = 0

        cumulative_tpt = 0
        cumulative_dl_tpt_values = []

        # Iterate through the keys of tpt
        for key in dl_tpt:
            cumulative_tpt += dl_tpt[key]
            if key % WINDOW_SIZE == 0:
                cumulative_dl_tpt_values.append(cumulative_tpt)
                cumulative_tpt = 0        


        # Plotting the cumulative TPT values
        ax3.plot(cumulative_ul_tpt_values, label='UL TPT')
        ax3.plot(cumulative_dl_tpt_values, label='DL TPT')

        # Adding labels and title
        ax3.set_xlabel('(TTI) Index')
        ax3.set_ylabel('TPT')
        ax3.set_title('UL and DL Traffic at capacity')

        # Adding legend
        ax3.legend()

        # Displaying the plot
        plt.tight_layout()
        plt.show()

        ## plot on the 4th subplot
        ax4 = axes[0, 3]

        # Plotting the cumulative CQI values
        ax4.plot(ul_cqi_values, label='UL CQI')

        # Adding labels and title
        ax4.set_xlabel('(TTI) Index')
        ax4.set_ylabel('CQI')
        ax4.set_title('UL CQI Variation')

        # Adding legend
        ax4.legend()

        # Displaying the plot
        plt.tight_layout()
        plt.show()

        ## plot 5th subplot

        ax5 = axes[1, 0]

        # Plotting the cumulative SNR values
        ax5.plot(ul_snr_values, label='UL SNR')

        # Adding labels and title
        ax5.set_xlabel('(TTI) Index')
        ax5.set_ylabel('SNR')
        ax5.set_title('UL SNR Variation')

        # Adding legend
        ax5.legend()

        # Displaying the plot
        plt.tight_layout()
        plt.show()

        # save 
        fig.savefig("plotting.png", format="png", dpi=150)

if __name__ == "__main__":
    

    thread_audoUE = threading.Thread(target=autoUE)

    thread_processDATA = threading.Thread(target=processDATA)

    thread_audoUE.start()
    thread_processDATA.start()

    thread_audoUE.join()
    thread_processDATA.join()

    print("Done!")