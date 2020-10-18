# Overview

## Build

```
$ docker build . -t registry-synchronizer:0.0.1
```

## Run (Docker out Docker)

```
$ docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/maps:/var/maps \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
  registry-synchronizer:0.0.1 --mapfile /var/maps/test.yaml [--concurrency = <file>]
```

## Debug

If something does not work as exspected, you may try to reproduce some steps from inside the container.

```
$ docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/maps:/var/maps \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
  --entrypoint /bin/sh \
  registry-synchronizer:0.0.1
```

Install CLI tools

```
$ apk add docker-cli
$ pip install awscli
```

Try to log into a registry

```
$ aws ecr get-login-password \
    --region eu-central-1 \
    --profile default | \
  docker login \
    --username AWS \
    --password-stdin 1234556789.dkr.ecr.eu-central-1.amazonaws.com
```
