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
2
```

<!-- ## Expected Output

![UE Output](working_ue.png, "UE") -->