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
docker build --target oai-gnb --file docker/Dockerfile.gNB.ubuntu22 -t my-oai-gnb-image .
```

### Build oai-nrue

```
docker build --target oai-nr-ue --file docker/Dockerfile.nrUE.ubuntu22 -t my-oai-nr-ue-image .
```

## Run The System

Go to the `tinytwin-oai/sims/siso` folder and bring up the services defined in the `docker-compose.yaml`.

### Bring Up the Core Network

```
sudo docker compose up -d mysql oai-amf oai-smf oai-ext-dn oai-upf
```

### Bring Up the nrUE

```
sudo docker compose up -d oai-nr-ue
```

### Bring Up the gNB

```
sudo docker compose up -d oai-gnb
```

### Run Traffic