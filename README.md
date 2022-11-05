# Easily set up passive income apps - Raspberry Pi

This repository revolves around a quick setup of passive income apps on a Raspberry Pi. Docker and docker-compose are used to make the process as quick and easy as possible. Docker allows for a rapid, isolated and clean install. 

The container automatically generates the required docker-compose file based on the desired apps that need to be installed.

Currently, the supported 'passive' income apps are:

1. Honeygain
2. Peer2profit
3. IPRoyal
4. PacketStream
5. Earnapp

## Prerequisites
It is asssumed that this will run on a Rasperry Pi that has docker installed along with docker-compose.

## Steps
The following command will retrieve the container and mount a local folder on the host to that container. The container will ask which services need to be installed and it will automatically generate the docker-compose based on the provided answers. The docker-compose will be made available and includes all required components to run successfully on a Raspberry Pi.

```BASH
docker run --rm -it -v $HOME/passive_yaml:/code/output passivepi/passive_earn:latest
```

Finally, run:

```BASH
docker-compose up -d & docker-compose logs -f
```

## Final thoughts
The efforts in this project have been focused at making the installation process as easy as possible. For this reason, Docker is utilized. Please remember however, that some of the apps are not built to run natively in containerized form on a Raspberry Pi. Usage is at own risk.
