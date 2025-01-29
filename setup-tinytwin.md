# tinytwin-oai

This document assumes you are in the `tinytwin-oai` folder.

## Build nrUE and gNB

```
cd cmake_targets/
# get rid of any previous installation
./build_oai -C
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
sudo ./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod
```

## Run OAI-nrUE (Seperate Terminal from gNB)

```
cd cmake_targets/ran_build/build/
sudo ./nr-uesoftmodem --uicc0.imsi 001010000000001 -C 3619200000 -r 106 --numerology 1 --ssb 516 -E --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf
```

<!-- ## Expected Output

![UE Output](working_ue.png, "UE") -->