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
            if len(words) >= 4:
                try:
                    float_value = float(words[3])  # Convert the 4th word to float
                    float_values.append(float_value)
                except ValueError:
                    print(f"Cannot convert '{words[3]}' to float on line {i}")
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
        time.sleep(10)
        os.system(f"docker exec -it -d tt-gnb  /opt/tt-ran/tt/cmake_targets/ran_build/build/nr-softmodem -O /opt/tt-ran/tt/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod --TAP 1 --TTI 1 --SNR 1")
        for i in range(151,151+kk):
            os.system(f"docker compose up -d tt-nrue{i}")
            time.sleep(min((i-150)*6,37))
                
        time.sleep(10)

        os.system(f"docker compose down")

        flag=0

def processDATA():
    global flag
    time.sleep(2)

    for kk in range(1,int(sys.argv[1])+1):
        flag=1
        while flag == 1:
            time.sleep(2)

        ### @ALI: things to consider:
        ### - this code block reads from a file saved from ending the execution of the gNB executable
        ### - this plots a single TTI plot, if you want to compare with other TTI plots, this is very scalable

        # read from TTI file
        ### @ALI: change this to whatever file you would like to point
        vals_1tap = read_starting("../../../logs/tti.txt")
        diff_tti_1tap = [vals_1tap[i] - vals_1tap[i - 1] for i in range(1, len(vals_1tap))]

        tti_1tap = np.array(diff_tti_1tap)
        mean_tti_1tap = np.mean(tti_1tap)

        size = 100000

        # CCDFs of various TTI times across 100,000 instances
        tti_1tap = tti_1tap[:size]
        sorted_tti_1tap = np.sort(tti_1tap)
        p1 = np.linspace(0, 1, len(tti_1tap))

        fig = plt.figure(figsize=(12, 8), dpi=150)
        ax2 = fig.add_subplot(111) 

        # plot CCDF
        ax2.plot(sorted_tti_1tap, 1 - p1, label='1 Tap', linewidth=2)

        # add a red vertical line at x=0.001 --> 3GPP TTI timing
        ax2.axvline(x=0.001, color='red', linestyle='--', linewidth=2)

        ax2.set_xlabel('TTI Times (s)', fontsize=14)
        ax2.set_ylabel('$CCDF$', fontsize=14)
        ax2.set_title('TTI Variation With Number Of Taps (CCDF)', fontsize=16)

        # Set x-axis limit
        ax2.set_xlim(0, 0.01)

        # Customize the grid
        ax2.grid(True, which='both', linestyle='--', linewidth=0.7, color='gray')

        # Add minor ticks for a finer grid
        ax2.minorticks_on()
        ax2.grid(which='minor', linestyle=':', linewidth=0.5, color='lightgray')

        ax2.legend()  # Add legend

        plt.savefig("tti_variation_ccdf.png", format="png", dpi=150)
        plt.show()

if __name__ == "__main__":
    

    thread_audoUE = threading.Thread(target=autoUE)

    thread_processDATA = threading.Thread(target=processDATA)

    thread_audoUE.start()
    thread_processDATA.start()

    thread_audoUE.join()
    thread_processDATA.join()

    print("Done!")