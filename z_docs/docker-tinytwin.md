# tinytwin-oai

This document assumes you are in the `tinytwin-oai` folder.

## Build Fresh Docker Images

Remove any existing OAI Docker images using `docker rmi`.

### Build ran-base

Contains all the dependencies used to run OAI.

```
docker build --target ran-base --tag ran-base:latest --file docker/Dockerfile.base.ubuntu22 .
```

### Run ran-build

Contains the compiled and linked executable to run the gNB and the UE.

```
docker build --target ran-build --tag ran-build:latest --file docker/Dockerfile.build.ubuntu22 .
```

### Build oai-gnb

```
docker build --target tt-gnb --file docker/tinytwin/Dockerfile.TTgNB.ubuntu22 -t tt-gnb:v2 .
```

### Build oai-nrue

```
docker build --target tt-nrue --file docker/tinytwin/Dockerfile.TTnrUE.ubuntu22 -t tt-nrue:v2 .
```

## Run The System

Go to the `tinytwin-oai/sims` folder and bring up the services defined in the appropriate `docker-compose.yaml` files.

### Bring Up the Core Network

```
cd oai-cn/
sudo docker compose up -d
```

### SISO

#### Bring Up the gNB

1. Bring up the Docker Container

```
cd siso
sudo docker compose up -d tt-gnb
```

2. Get into the Docker container 

```
docker exec -it tt-gnb bash
```

3. Build the system

```
cd /opt/tt-ran/tt/cmake_targets/ran_build/build/
./build_oai -C # gets rid of any existing installation
./build_oai -I -w SIMU --nrUE --gNB # builds dependencies and the rfsim gNB and UEs
```

4. Run the gNB executable

```
./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --rfsim -E --sa  --rfsimulator.options chanmod --TAP 1 --TTI 1 --SNR 1
```


#### Bring Up the nrUE

1. Bring up the Docker Container

```
sudo docker compose up -d tt-nrue1
```

You can bring up multiple UEs (upto 6 already defined in this `docker-compose.yaml`) connected to the same gNB in the same way as this. The NR UEs come with the OAI system already compiled and ready to run.

_NOTE: Only bring up a fresh UE after the current UE has been connected._

2. (Optional) Run the UE executable

```
./nr-uesoftmodem --uicc0.imsi 001010000000001 -C 3619200000 -r 106 --numerology 1 --ssb 516 -E --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf --TAP 1 --rfsimulator.serveraddr 192.168.70.140
```

### MIMO

#### Bring Up the gNB

1. Bring up the Docker Container

```
cd mimo
sudo docker compose up -d tt-mimo-gnb
```

2. Get into the Docker container 

```
docker exec -it tt-mimo-gnb bash
```

3. Build the system

```
cd /opt/tt-ran/tt/cmake_targets/ran_build/build/
./build_oai -C # gets rid of any existing installation
./build_oai -I -w SIMU --nrUE --gNB # builds dependencies and the rfsim gNB and UEs
```

4. Run the gNB executable

```
./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.162PRB.2x2.usrpn300.conf --rfsim --sa  --rfsimulator.options chanmod --TAP 1
```


#### Bring Up the nrUE

1. Bring up the Docker Container

```
sudo docker compose up -d tt-mimo-nrue1
```

You can bring up multiple UEs (upto 6 already defined in this `docker-compose.yaml`) connected to the same gNB in the same way as this. The NR UEs come with the OAI system already compiled and ready to run.

_NOTE: Only bring up a fresh UE after the current UE has been connected._

2. (Optional) Run the UE executable

```
./nr-uesoftmodem --uicc0.imsi 001010000000001 -C 3329760000 -r 162 --numerology 1 --ssb 852 --sa --rfsim --rfsimulator.options chanmod -O ../../../ci-scripts/conf_files/nrue.uicc.conf --TAP 1 --rfsimulator.serveraddr 192.168.70.140 --ue-nb-ant-tx 2 --ue-nb-ant-rx 2 --uecap_file ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/uecap_ports2.xml
```

