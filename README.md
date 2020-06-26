# Traefik CertDumper

to dump letsencrypt certificates (full chain) with private key from JSON file storage (Traefik v2.2).


### Table of Contents
**[Usage Instructions](#usage-instructions)**<br>
**[Building Image](#building-image)**<br>
**[Feedback](#feedback)**<br>


## Usage Instructions

#### Storage

You need to mount the volume with the destination of `/traefik` which will contains `acme.json` file.

This container will create directory named `ssl/certs` for certificates and `ssl/private` for private keys for correcsponding certificates under `/traefik` directory.


#### Deploy Containers

```bash
sudo docker run -itd --rm -v traefik_data:/traefik apandiyan/traefik-certdumper:v0.1
```

Using docker volume traefik_data to store letsencrypt certificates and for dumping.


#### Deploy container using docker-compose

```bash
sudo docker-compose -p axigen -f docker-compose.yml up -d
```

You can change docker-compose.yml as per your need

```yaml
version: '3.7'
services:
  axigen:
    image: apandiyan/traefik-certdumper:v0.1
    command: sh -c "while true; do python run.py && sleep 6h ; done"
    volumes:
      - traefik_data:/traefik

volumes:
  traefik_data:
```

#### Deploy service on docker swarm along-with traefik

Request you to make sure changing of email address to be configured as account with letsencrypt and domain name before using it.

```yaml
version: '3.7'

services:
  traefik:
    image: traefik:v2.2.1
    command:
      - "--api=true"
      - "--api.insecure=true"
      - "--ping=true"
      # - "--accesslog=true"
      - "--providers.docker=true"
      - "--providers.docker.swarmmode=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.docker.network=traefik-public"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.le.acme.email=${EMAIL}"
      - "--certificatesresolvers.le.acme.storage=/traefik/acme.json"
      - "--certificatesresolvers.le.acme.httpchallenge=true"
      - "--certificatesresolvers.le.acme.httpchallenge.entrypoint=web"
      # - "--certificatesresolvers.le.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
    ports:
      - mode: host
        published: 80
        target: 80
      - mode: host
        published: 443
        target: 443
    volumes:
      - traefik_data:/traefik
      - /var/run/docker.sock:/var/run/docker.sock:ro
    secrets:
      - traefik-htpasswd
    healthcheck:
      test: ["CMD", "traefik", "healthcheck", "--ping", "||", "exit", "1"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 1m
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      labels:
        - "traefik.enable=true"
        # web entrypoint
        - "traefik.http.routers.traefik.rule=Host(`traefik.localhost`)"
        - "traefik.http.routers.traefik.entrypoints=web"
        - "traefik.http.routers.traefik.service=traefik@docker"
        - "traefik.http.services.traefik.loadbalancer.server.port=8080"
        # websecure entrypoint
        - "traefik.http.routers.traefik-secure.rule=Host(`traefik.localhost`)"
        - "traefik.http.routers.traefik-secure.entrypoints=websecure"
        - "traefik.http.routers.traefik-secure.service=traefik@docker"
        - "traefik.http.services.traefik-secure.loadbalancer.server.port=8080"
        - "traefik.http.routers.traefik-secure.tls=true"
        - "traefik.http.routers.traefik-secure.tls.certresolver=le"
        # web to websecure redirection
        - "traefik.http.routers.traefik.middlewares=https-redirect"
        - "traefik.http.middlewares.https-redirect.redirectscheme.scheme=https"
        - "traefik.http.middlewares.https-redirect.redirectscheme.permanent=true"
        # enable basicauth on websecure
        - "traefik.http.routers.traefik-secure.middlewares=traefik-auth"
        - "traefik.http.middlewares.traefik-auth.basicauth.usersfile=/run/secrets/traefik-htpasswd"
    networks:
      - traefik-public
  certdumper:
    image: apandiyan/traefik-certdumper
    volumes:
      - traefik_data:/traefik
    command: sh -c "while true; do python run.py && sleep 6h ; done"
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      update_config:
        failure_action: rollback
        order: start-first
      rollback_config:
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 10s
        window: 60s

networks:
  traefik-public:
    external: true

secrets:
  traefik-htpasswd:
    file: ./traefik-htpasswd
```

```bash
sudo docker stack deploy -c docker-compose.yml loadbalancer
```


## Building Image

```bash
git clone https://github.com/apandiyan/traefik-certdumper.git
cd traefik-certdumper
sudo docker image build -t apandiyan/traefik-certdumper:v0.1 .
```

You can download source from [Github](https://github.com/apandiyan/traefik-certdumper.git) and build image using docker build command.


## Feedback

All bugs, feature requests, pull requests, feedback, etc., are welcome. [Create an issue](https://github.com/apandiyan/traefik-certdumper/issues).
