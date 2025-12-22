import sys
import os
import time
import threading
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 

start_ue = int(sys.argv[1])
end_ue = int(sys.argv[1])

start_tap = int(sys.argv[2])
end_tap = int(sys.argv[2])

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
            - ./stop.sh:/opt/tt-ran/stop.sh
            - ./build.sh:/opt/tt-ran/build.sh
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
    edgeric:
        container_name: edgeric_v2_2
        # Build info
        image: edgeric/v2
        build:
            context: edgeric-v2
            dockerfile: ../Dockerfile-edgeric
            args:
                OS_VERSION: "24.04"
        # privileged mode is requred only for accessing usb devices
        privileged: true
        ports:
            - "7000:7000"
        # entrypoint: ["/home/EdgeRIC-A-real-time-RIC/srsran_entrypoint.sh"]
        # Extra capabilities always required
        cap_add:
            - SYS_NICE
            - CAP_SYS_PTRACE
        volumes:
            # - ${pwd}/radio_network:/home/EdgeRIC-A-real-time-RIC:rw
            - /tmp/.X11-unix:/tmp/.X11-unix:rw
            - /dev:/dev
            # - ${PWD:-.}:/home/EdgeRIC-A-real-time-RIC:rw
            - ./edgeric-v2:/home/EdgeRIC:rw
        # It creates a file/folder into /config_name inside the container
        # Its content would be the value of the file used to create the config
        # configs:
        #   - gnb_config.yml
        # Customize your desired network mode.
        # current netowrk configuration creastes a private netwoek with both containers attached
        # An alterantive would be `network: host"`. That would expose your host network into the container. It's the easiest to use if the 5gc is not in your PC
        networks:
            public_net:
                ipv4_address: 192.168.70.166
        # Start GNB container after 5gc is up and running
        # depends_on:
        #   gnb:
        #     condition: service_healthy


networks:
    public_net:
        driver: bridge
        external: true
        name:  oai-cn5g-public-net
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

    all_vals = {}

    ul_snr_values = []
    ul_mcs_values = []
    dl_mcs_values = []
    ul_tpt_values = []
    dl_tpt_values = []
    ul_cqi_values = []
    ul_ack_values = []
    dl_ack_values = []

    ul_snr_ttis = []
    ul_mcs_ttis = []
    dl_mcs_ttis = []
    ul_tpt_ttis = []
    dl_tpt_ttis = []
    ul_cqi_ttis = []
    ul_ack_ttis = []
    dl_ack_ttis = []

    all_metrics = [
    ul_snr_values, ul_mcs_values, dl_mcs_values, ul_tpt_values, dl_tpt_values,
    ul_cqi_values, ul_ack_values, dl_ack_values,
    ul_snr_ttis, ul_mcs_ttis, dl_mcs_ttis, ul_tpt_ttis, dl_tpt_ttis,
    ul_cqi_ttis, ul_ack_ttis, dl_ack_ttis
    ]

    previous_line = None

    with open(file_name, 'r') as f:
        for i, line in enumerate(f, start=1):
            # if (i-1) % 2 == 0:
            words = line.split()
            if len(words) >= 3:
                try:
                    float_value = float(words[2])  # Convert the last word to float
                    if words[0] == 'UL':
                        rnti = words[-1]
                        if rnti not in all_vals.keys():
                            # all_vals[rnti] = {name: [] for name in all_metrics}  # Initialize metric lists
                            all_vals[rnti] = {name: [] for name in [
                                'ul_snr_values', 'ul_mcs_values', 'dl_mcs_values', 'ul_tpt_values', 'dl_tpt_values',
                                'ul_cqi_values', 'ul_ack_values', 'dl_ack_values',
                                'ul_snr_ttis', 'ul_mcs_ttis', 'dl_mcs_ttis', 'ul_tpt_ttis', 'dl_tpt_ttis',
                                'ul_cqi_ttis', 'ul_ack_ttis', 'dl_ack_ttis'
                            ]}  # Initialize metric lists
                        
                        # while(1){    
                        #     rnti = float(words[4])
                        #     if rnti in all_vals.keys():
                        #         break
                        #     else:
                        #         all_vals[rnti] = {name: [] for name in all_metrics}    
                        # }

                        if words[1] == 'SNR:':
                            # refer to previous line
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['ul_snr_ttis'].append(tti)
                            all_vals[rnti]['ul_snr_values'].append(float_value)
                        elif words[1] == 'MCS:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['ul_mcs_ttis'].append(tti)
                            all_vals[rnti]['ul_mcs_values'].append(float_value)
                        elif words[1] == 'TPT:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['ul_tpt_ttis'].append(tti)
                            all_vals[rnti]['ul_tpt_values'].append(float_value)
                        elif words[1] == 'CQI:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['ul_cqi_ttis'].append(tti)
                            all_vals[rnti]['ul_cqi_values'].append(float_value)
                        elif words[1] == 'ACK:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['ul_ack_ttis'].append(tti)
                            all_vals[rnti]['ul_ack_values'].append(float_value)
                    elif words[0] == 'DL':
                        rnti = words[-1]
                        if rnti not in all_vals.keys():
                            all_vals[rnti] = {name: [] for name in [
                                'ul_snr_values', 'ul_mcs_values', 'dl_mcs_values', 'ul_tpt_values', 'dl_tpt_values',
                                'ul_cqi_values', 'ul_ack_values', 'dl_ack_values',
                                'ul_snr_ttis', 'ul_mcs_ttis', 'dl_mcs_ttis', 'ul_tpt_ttis', 'dl_tpt_ttis',
                                'ul_cqi_ttis', 'ul_ack_ttis', 'dl_ack_ttis'
                            ]}  # Initialize metric lists
                        if words[1] == 'MCS:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['dl_mcs_ttis'].append(tti)
                            all_vals[rnti]['dl_mcs_values'].append(float_value)
                        elif words[1] == 'TPT:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['dl_tpt_ttis'].append(tti)
                            all_vals[rnti]['dl_tpt_values'].append(float_value)
                        elif words[1] == 'ACK:':
                            if previous_line:
                                ttis = previous_line.split()
                                tti = int(ttis[2])
                                all_vals[rnti]['dl_ack_ttis'].append(tti)
                            all_vals[rnti]['dl_ack_values'].append(float_value)
                except ValueError:
                    print(f"Cannot convert '{words[-1]}' to float on line {i}")
            else:
                print(f"Line {i} does not have 1 word...")
            previous_line = line
    # return ul_snr_values, ul_snr_values, ul_cqi_values, ul_cqi_ttis, ul_mcs_values, ul_mcs_ttis, dl_mcs_values, dl_mcs_ttis, ul_tpt_values, ul_tpt_ttis, dl_tpt_values, dl_tpt_ttis, ul_ack_values, ul_ack_ttis, dl_ack_values, dl_ack_ttis
    return all_vals

def Convert(snr_ttis, snr_values):
    res_dct = {snr_ttis[i]: snr_values[i] for i in range(len(snr_ttis))}
    return res_dct

def create_docker(i, n_tap):
    template=f'''
    tt-nrue{i-160}:
        image: tt-nrue:v2
        container_name: tt-ue{i-160}
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
            ./nr-uesoftmodem --uicc0.imsi 0010100000000{i-150} -C 3619200000 -r 106 --numerology 1 --ssb 516 -E --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf --TAP {n_tap} --rfsimulator.serveraddr 192.168.70.140 &&
            exec /bin/bash"
        # entrypoint: /bin/bash
        stdin_open: true  
        tty: true        
        networks:
            public_net:
                ipv4_address: 192.168.70.{i-10}
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
    for ktap in range(start_tap,end_tap+1,4):
        for kk in range(start_ue,end_ue+1,3):
            os.makedirs(f"./plot/ue{kk}_{ktap}", exist_ok=True)
            os.system("cp /home/wcsng5g/tinytwin-oai/channel/channel_clean_demo2.txt /home/wcsng5g/tinytwin-oai/channel/channel_clean.txt ")
            time.sleep(10)
            os.system("docker compose -f ../../oai-cn/docker-compose.yaml up -d")
            os.system("docker compose -f /home/wcsng5g/tinytwin-oai/sims/siso/tti_experiments/edgeric-v2/muApp3/docker/prometheus/docker-compose.yml up -d")
            os.system("docker compose -f /home/wcsng5g/tinytwin-oai/sims/siso/tti_experiments/edgeric-v2/muApp3/docker/grafana/docker-compose.yml up -d")
            while flag == 0:
                time.sleep(2)
            

            file=""
            for i in range(161,161+kk):
                file=file+"\n"+create_docker(i,ktap)
            file = start+ file+ end
            print(file)

            
            with open("./docker-compose.yaml","+w") as f:
                f.write(file)
            os.system(f"docker compose up -d tt-gnb")
            time.sleep(10)
            os.system(f"docker compose up -d edgeric")
            print("set up ran")
            time.sleep(10)
            os.system(f"docker exec -d edgeric_v2_2 python3 ./muApp3/muApp3_monitor_grafana.py ")
            os.system(f"docker exec tt-gnb chmod +x run.sh build.sh")
            os.system(f"docker exec -d tt-gnb ./run.sh ")
            #os.system(f"docker exec -d tt-gnb  cd /opt/tt-ran/tt/cmake_targets/ran_build/build/ && ./nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod --TAP 1 --TTI 1 --SNR 1 --MCS 1 --CQI 1 --TPT 1")
            for i in range(161,161+kk):
                os.system(f"docker compose up -d tt-nrue{i-160}")
                time.sleep(min((i-160)*12,15))
                #os.system(f"docker exec -it tt-ue{i} ifconfig oaitun_ue1| grep 'inet ' ")

            # for jk in range(161,161+kk): 
            #     os.system(f"""docker exec -d oai-ext-dn bash -c "ping 10.0.0.{jk-159} -c 50 > ./dl_ue{jk-160}.txt" """)
            #     os.system(f"""docker exec -d tt-ue{jk-160} bash -c "ping 10.0.0.1 -c 50 > ./ul_ue{jk-160}.txt" """)
            # time.sleep(1)
            # os.system(f"""top -bn6 > ./plot/ue{kk}_{ktap}/ping_cpumem.txt """)
            # time.sleep(6)


            # for jk in range(161,161+kk): 
            #     os.system(f"docker cp oai-ext-dn:/tmp/dl_ue{jk-160}.txt ./plot/ue{kk}_{ktap}/dl_ue{jk-160}.txt")
            #     os.system(f"docker cp tt-ue{jk-160}:/opt/tt-ran/ul_ue{jk-160}.txt ./plot/ue{kk}_{ktap}/ul_ue{jk-160}.txt")

            for ik in range(161,161+kk): 
                os.system(f"docker exec -d tt-ue{ik-160} iperf -s -u -i 1 -B 10.0.0.{ik-159} ")
                os.system(f"docker exec -d oai-ext-dn iperf -s -i 1 -B 192.168.70.135 -p 52{ik-149}")
            time.sleep(2)
            for jk in range(161,161+kk): 
                os.system(f"docker exec -d oai-ext-dn iperf -u -t 86400 -i 1 -fk -B 192.168.70.135 -b 3M -c 10.0.0.{jk-159}")
                os.system(f"docker exec -d tt-ue{jk-160} iperf -t 86400 -i 1 -fk -c 192.168.70.135 -b 3.5M -B 10.0.0.{jk-159} -p 52{ik-149}")
            time.sleep(5)
            os.system(f"""top -bn6 > ./plot/ue{kk}_{ktap}/iperf_cpumem.txt """)
            #test
            time.sleep(20)
            os.system(f"docker exec -d edgeric_v2_2 python3 send_weight_demo21.py")
            pid = subprocess.check_output(
                ["docker", "exec", "edgeric_v2_2", "pgrep", "-f", "send_"]
            ).decode().strip()

            print("PID:", pid)
            time.sleep(130)
            os.system(f"docker exec -d edgeric_v2_2 kill -9 {pid} ")
            time.sleep(5)
            os.system(f"docker exec -d edgeric_v2_2 python3 send_weight_demo22.py")
            time.sleep(130)

            print("kill gnb")
            os.system(f"docker exec tt-gnb chmod +x stop.sh ")
            os.system(f"docker exec -d tt-gnb ./stop.sh ")
            time.sleep(5)

            os.system(f"docker compose down")
            os.system("docker compose -f /home/wcsng5g/tinytwin-oai/sims/siso/tti_experiments/edgeric-v2/muApp3/docker/grafana/docker-compose.yml down")
            os.system("docker compose -f /home/wcsng5g/tinytwin-oai/sims/siso/tti_experiments/edgeric-v2/muApp3/docker/prometheus/docker-compose.yml down")
            os.system("docker compose -f ../../oai-cn/docker-compose.yaml down")


            flag=0
        
    

def processDATA():
    global flag
    time.sleep(2)

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

    for ktap in range(start_tap,end_tap+1,4):

        for kk in range(start_ue,end_ue+1,3):

            flag=1
            while flag == 1:
                time.sleep(2)

            # # read from TTI file
            # ### @ALI: change this to whatever file you would like to point
            # vals_tti = read_starting("../../../logs/tti.txt")
            # diff_tti = [vals_tti[i] - vals_tti[i - 1] for i in range(1, len(vals_tti))]
            # diff_tti = [diff_tti[i]/1000000000 for i in range(1, len(diff_tti))]

            # tti = np.array(diff_tti)
            # tti = [max(0, tti_val) for tti_val in tti]
            # # remove all zero values
            # tti = [tti_val for tti_val in tti if tti_val > 0]
            # mean_tti = np.mean(tti)

            # size = 100000

            # # CCDFs of various TTI times across 100,000 instances
            # tti = tti[:size]
            # sorted_tti = np.sort(tti)
            # p1 = np.linspace(0, 1, len(tti))

            # # 8 subplots
            # fig, axes = plt.subplots(2, 4, figsize=(20, 10), dpi=150)

            # # plot CCDF
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

            # plt.savefig("tti_variation_ccdf.png", format="png", dpi=150)

            # ### read MAC metrics
            # # define all_vals

            # # ul_snr_values = []
            # # ul_mcs_values = []
            # # dl_mcs_values = []
            # # ul_tpt_values = []
            # # dl_tpt_values = []
            # # ul_cqi_values = []

            # # ul_snr_ttis = []
            # # ul_mcs_ttis = []
            # # dl_mcs_ttis = []
            # # ul_tpt_ttis = []
            # # dl_tpt_ttis = []
            # # ul_cqi_ttis = []

            # all_vals = read_more("../../../logs/snr.txt")

            # # ul_snr_values_a.append(ul_snr_values)
            # # ul_mcs_values_a.append(ul_mcs_values)
            # # dl_mcs_values_a.append(dl_mcs_values)
            # # ul_tpt_values_a.append(ul_tpt_values)
            # # dl_tpt_values_a.append(dl_tpt_values)
            # # ul_cqi_values_a.append(ul_cqi_values)

            # # ul_snr_ttis_a.append(ul_snr_ttis)
            # # ul_mcs_ttis_a.append(ul_mcs_ttis)
            # # dl_mcs_ttis_a.append(dl_mcs_ttis)
            # # ul_tpt_ttis_a.append(ul_tpt_ttis)
            # # dl_tpt_ttis_a.append(dl_tpt_ttis)
            # # ul_cqi_ttis_a.append(ul_cqi_ttis)

            # # Plot on the second subplot (0, 1)
            # ax2 = axes[0, 1]

            # for rnti in all_vals.keys():
            #     ax2.plot(all_vals[rnti]['ul_mcs_ttis'], all_vals[rnti]['ul_mcs_values'], label=f'{rnti} UL MCS')
            #     ax2.plot(all_vals[rnti]['dl_mcs_ttis'], all_vals[rnti]['dl_mcs_values'], label=f'{rnti} DL MCS')

            # # Adding labels and title
            # ax2.set_xlabel('(TTI) Index')
            # ax2.set_ylabel('MCS')
            # ax2.set_title('MCS Variation')

            # # Adding legend
            # ax2.legend()

            # # Displaying the plot
            # # plt.tight_layout()
            # # plt.show()

            # cumulative_dl_tpt_values = []
            # cumulative_ul_tpt_values = []

            # # # Plot on the third subplot (0, 2)
            # # ax3 = axes[0, 2]
            
            # # # ul_cumulative = []
            # # # dl_cumulative = []
            # # # for rnti in all_vals.keys():
            # # #     # Assuming tpt_ttis and tpt_values are already defined
            # # #     ul_tpt = Convert(all_vals[rnti]['ul_tpt_ttis'], all_vals[rnti]['ul_tpt_values'])
            # # #     dl_tpt = Convert(all_vals[rnti]['dl_tpt_ttis'], all_vals[rnti]['dl_tpt_values'])

            # # WINDOW_SIZE = 1000
            # # cumulative_tpt = 0

            # # # Iterate through the keys of tpt
            # # for key in ul_tpt:
            # #     for rnti in 
            # #     cumulative_tpt += ul_tpt[key]
            # #     if key % WINDOW_SIZE == 0:
            # #         cumulative_ul_tpt_values.append(cumulative_tpt)
            # #         cumulative_tpt = 0

            # #     cumulative_tpt = 0

            # #     # Iterate through the keys of tpt
            # #     for key in dl_tpt:
            # #         cumulative_tpt += dl_tpt[key]
            # #         if key % WINDOW_SIZE == 0:
            # #             cumulative_dl_tpt_values.append(cumulative_tpt)
            # #             cumulative_tpt = 0   




            # # # Plotting the cumulative TPT values
            # # ax3.plot(ul, label='UL TPT')
            # # ax3.plot(dl, label='DL TPT')

            # # # Adding labels and title
            # # ax3.set_xlabel('(TTI) Index')
            # # ax3.set_ylabel('TPT')
            # # ax3.set_title('UL and DL Traffic at capacity')

            # # # Adding legend
            # # ax3.legend()

            # # plotting on the fourth plot
            # ax4 = axes[0, 3]

            # for rnti in all_vals.keys():
            #     ax4.plot(all_vals[rnti]['ul_tpt_ttis'], all_vals[rnti]['ul_tpt_values'], label=f'{rnti} UL TPT')
            #     ax4.plot(all_vals[rnti]['dl_tpt_ttis'], all_vals[rnti]['dl_tpt_values'], label=f'{rnti} DL TPT')

            # # Adding labels and title
            # ax4.set_xlabel('(TTI) Index')
            # ax4.set_ylabel('Bytes')
            # ax4.set_title('Per UE Throughput Variation')

            # # Adding legend
            # ax4.legend()

            # ## plot on the 5th subplot
            # ax5 = axes[1, 0]

            # # Plotting the cumulative CQI values
            # for rnti in all_vals.keys():
            #     ax5.plot(all_vals[rnti]['ul_cqi_ttis'], all_vals[rnti]['ul_cqi_values'], label=f'{rnti} UL CQI')

            # # Adding labels and title
            # ax5.set_xlabel('(TTI) Index')
            # ax5.set_ylabel('CQI')
            # ax5.set_title('UL CQI Variation')

            # # Adding legend
            # ax5.legend()

            # # Displaying the plot
            # # plt.tight_layout()
            # # plt.show()

            # ## plot 6th subplot
            # ax6 = axes[1, 1]

            # # Plotting the cumulative SNR values
            # for rnti in all_vals.keys():
            #     ax6.plot(all_vals[rnti]['ul_snr_ttis'], all_vals[rnti]['ul_snr_values'], label=f'{rnti} UL SNR')
            #     # ax5.plot(ul_snr_values, label='UL SNR')

            # # Adding labels and title
            # ax6.set_xlabel('(TTI) Index')
            # ax6.set_ylabel('SNR')
            # ax6.set_title('UL SNR Variation')

            # # Adding legend
            # ax6.legend()

            # # Displaying the plot
            # # plt.tight_layout()
            # # plt.show()

            # ## plot 6th subplot
            # ax7 = axes[1, 2]

            # # Plotting the ACK status
            # for rnti in all_vals.keys():
            #     ax7.plot(all_vals[rnti]['ul_ack_ttis'], all_vals[rnti]['ul_ack_values'], label=f'{rnti} UL ACKs')
            #     ax7.plot(all_vals[rnti]['dl_ack_ttis'], all_vals[rnti]['dl_ack_values'], label=f'{rnti} DL ACKs')

            # # Adding labels and title
            # ax7.set_xlabel('(TTI) Index')
            # ax7.set_ylabel('ACKs')
            # ax7.set_title('ACK Status')

            # # Adding legend
            # ax7.legend()

            # # Displaying the plot
            # # plt.tight_layout()
            # # plt.show()

            # fig.savefig("plotting.png", format="png", dpi=150)

            #os.system(f"mkdir ./plot/ue{kk}_{sys.argv[2]}")
            
            os.system(f"cp ../../../logs/tti.txt ./plot/ue{kk}_{ktap}/tti.txt")
            os.system(f"cp ../../../logs/snr.txt ./plot/ue{kk}_{ktap}/snr.txt")
            # os.system(f"cp plotting.png ./plot/ue{kk}_{ktap}/plotting.png")

if __name__ == "__main__":
    

    thread_audoUE = threading.Thread(target=autoUE)

    thread_processDATA = threading.Thread(target=processDATA)

    thread_audoUE.start()
    thread_processDATA.start()

    thread_audoUE.join()
    thread_processDATA.join()

    print("Done!")