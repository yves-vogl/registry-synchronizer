# About

Ever needed to migrate or even keep different AWS ECR registries synchronized?
Also during the phase of restructuring so that Container Repository names changed?

## Getting started

*DO NOT USE THIS IN PRODUCTION AS IT'S IN EARLY ALPHA STATE*

### Configure Mapfile

You first need to setup the map which specifies the source („from“) and target („to“) registry.
The process then will get the repositories from the target registry and look up the corresponding
names in the source registry. If the name of the image matches, all of its tags will be transfer to the target repository.
You also may apply one or more transformations on the name for comparison - the first matching transformation then stops.

See ```maps/example.yaml``` for details.

#### Authentication

When running locally from Python, you may set ```aws_profile_name``` in the map to use existing AWS credential profiles.

If running in a container you need to specify at least have the following environment variables set: ```AWS_ACCESS_KEY_ID``` and ```AWS_SECRET_ACCESS_KEY```.

You optionally may set ```AWS_SESSION_TOKEN``` and ```AWS_REGION``` (which defaults to ```eu-central-1```).


### Run from Python

Install prerequisites

```
pip3 install -r requirements.txt
```

#### Standalone

```
python3 app/main.py --mapfile maps/example.yaml [--concurrency 5]
```

#### Create jobs for Redis

```
python3 app/main.py --mapfile maps/example.yaml [--concurrency 5] --queue
```

#### Run the worker

```
python3 app/main.py [--concurrency 5] --worker
```

### Run from Docker


#### Build

```
$ docker build . -t registry-synchronizer:latest
```

#### Run (Docker out Docker)

```
$ docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/maps:/var/maps \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
  -e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
  registry-synchronizer:latest--mapfile /var/maps/test.yaml [--concurrency = <file>]
```

##### Debug

If something does not work as exspected, you may try to reproduce some steps from inside the container.

###### Prepare

```
$ docker run -it -rm \
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

###### Test

Try to log into a registry

```
$ aws ecr get-login-password \
    --region eu-central-1 \
    --profile default | \
  docker login \
    --username AWS \
    --password-stdin 1234556789.dkr.ecr.eu-central-1.amazonaws.com
```


# Known issues

The process progess output seems to have an issue with math ;-)

```
123145754238976: Pushing 59e4d73018b3: 100.4% -30902B
123145754238976: Pushing ba9f8a995b1e: 213.2% -2718B
```
