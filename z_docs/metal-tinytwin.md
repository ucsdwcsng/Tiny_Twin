# tinytwin-oai

This document assumes you are in the `tinytwin-oai` folder.

## Build nrUE and gNB

```
cd cmake_targets/
# get rid of any previous installation
./build_oai -C
# compile all dependencies along with the UE and the gNB
./build_oai -I --gNB --nrUE
```

## Run Core Network

```
cd oai-cng/
# core network will run in the background
docker compose up -d
```

You can stop the core network using `docker compose down`.

## Run OAI-gNB (Seperate Terminal from nrUE)

```
cd cmake_targets/ran_build/build/
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod -T 10
```

## Run OAI-nrUE (Seperate Terminal from gNB)

```
cd cmake_targets/ran_build/build/
sudo ./nr-uesoftmodem --uicc0.imsi 001010000000001 -C 3619200000 -r 106 --numerology 1 --ssb 516 -E --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf -T 10 
```

## Run DL Traffic

### Server

```
iperf -s -u -i 1 -B 10.0.0.2
```

### Client

```
docker exec -it oai-ext-dn iperf -u -t 86400 -i 1 -fk -B 192.168.70.135 -b 20M -c 10.0.0.8
```

## Run UL Traffic

### Server

```
docker exec -it oai-ext-dn iperf -s -u -i 1 -B 192.168.70.135
```

### Client

```
iperf -u -t 86400 -i 1 -fk -c 192.168.70.135 -b 20M -B 10.0.0.8
```


<!-- ## Expected Output

![UE Output](working_ue.png, "UE") -->