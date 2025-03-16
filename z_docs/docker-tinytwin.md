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

Go to the `tinytwin-oai/sims/siso` folder and bring up the services defined in the `docker-compose.yaml`.

### Bring Up the Core Network

```
sudo docker compose up -d mysql oai-amf oai-smf oai-ext-dn oai-upf
```

### Bring Up the gNB

```
sudo docker compose up -d oai-gnb
```

### Bring Up the nrUE

```
sudo docker compose up -d oai-nr-ue
```

### Run Traffic