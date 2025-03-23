import sys
import os
import time
start='''
services:

'''
end='''

networks:
    public_net:
        driver: bridge
        external: true
        name: tt-public-net
'''

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
            # - ../../channel/channel.txt:/opt/tt-ran/channel/channel_gradual.txt
            - ../../../ci-scripts/conf_files/nrue.uicc.conf:/opt/oai-nr-ue/etc/nr-ue.conf
            - ../../../logs_ue:/opt/oai-nr-ue/etc/logs
        entrypoint: >
            /bin/bash -c "ls && cd tt/cmake_targets/ran_build/build/ &&
            ./nr-uesoftmodem --uicc0.imsi 001010000000{i} -C 3619200000 -r 106 --numerology 1 --ssb 516 -E --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf --TAP {int(sys.argv[2])} --rfsimulator.serveraddr 192.168.70.140 &&
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
if __name__ == "__main__":
    file=""
    for i in range(150,150+int(sys.argv[1])):
        file=file+"\n"+create_docker(i)
    file = start+ file+ end
    print(file)

    with open("./docker-compose.yaml","+w") as f:
        f.write(file)
    for i in range(150,150+int(sys.argv[1])):
        os.system(f"docker compose up -d tt-nrue{i}")
        time.sleep(10)
    