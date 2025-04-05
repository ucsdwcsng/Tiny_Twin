import sys
import os
import time
import threading
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
start_ue = 1
end_ue = int(sys.argv[1])
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

def create_docker(i):
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
            ./nr-uesoftmodem --uicc0.imsi 0010100000000{i-150} -C 3619200000 -r 106 --numerology 1 --ssb 516 -E --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf --TAP {sys.argv[2]} --rfsimulator.serveraddr 192.168.70.140 &&
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
    
    for kk in range(start_ue,end_ue+1,3):
        os.system("docker compose -f ../../oai-cn/docker-compose.yaml up -d")
        while flag == 0:
            time.sleep(2)
        

        file=""
        for i in range(161,161+kk):
            file=file+"\n"+create_docker(i)
        file = start+ file+ end
        print(file)

        
        with open("./docker-compose.yaml","+w") as f:
            f.write(file)
        os.system(f"docker compose up -d tt-gnb")
        print("set up ran")
        time.sleep(10)
        os.system(f"docker exec tt-gnb chmod +x run.sh build.sh")
        os.system(f"docker exec -d tt-gnb ./run.sh ")
        #os.system(f"docker exec -d tt-gnb  cd /opt/tt-ran/tt/cmake_targets/ran_build/build/ && ./nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod --TAP 1 --TTI 1 --SNR 1 --MCS 1 --CQI 1 --TPT 1")
        for i in range(161,161+kk):
            os.system(f"docker compose up -d tt-nrue{i-160}")
            time.sleep(min((i-160)*12,15))
            #os.system(f"docker exec -it tt-ue{i} ifconfig oaitun_ue1| grep 'inet ' ")

        for jk in range(161,161+kk): 
            os.system(f"""docker exec -d oai-ext-dn bash -c "ping 10.0.0.{jk-159} -c 50 > ./dl_ue{jk-160}.txt" """)
            os.system(f"""docker exec -d tt-ue{jk-160} bash -c "ping 10.0.0.1 -c 50 > ./ul_ue{jk-160}.txt" """)

        #test
        time.sleep(100)

        for jk in range(161,161+kk): 
            os.system(f"docker cp oai-ext-dn:/tmp/dl_ue{jk-160}.txt ./plot/ue{kk}_{sys.argv[2]}/dl_ue{jk-160}.txt")
            os.system(f"docker cp tt-ue{jk-160}:/opt/tt-ran/ul_ue{jk-160}.txt ./plot/ue{kk}_{sys.argv[2]}/ul_ue{jk-160}.txt")

        time.sleep(100)

        print("kill gnb")
        os.system(f"docker exec tt-gnb chmod +x stop.sh ")
        os.system(f"docker exec -d tt-gnb ./stop.sh ")
        time.sleep(5)

        os.system(f"docker compose down")
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

    for kk in range(start_ue,end_ue+1,3):

        flag=1
        while flag == 1:
            time.sleep(2)

       

if __name__ == "__main__":
    

    thread_audoUE = threading.Thread(target=autoUE)

    thread_processDATA = threading.Thread(target=processDATA)

    thread_audoUE.start()
    thread_processDATA.start()

    thread_audoUE.join()
    thread_processDATA.join()

    print("Done!")