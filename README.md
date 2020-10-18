# About

Ever needed to migrate or even keep different AWS ECR registries synchronized?
Also during the phase of restructuring so that Container Repository names changed?

## Usage

*DO NOT USE THIS IN PRODUCTION AS IT'S IN EARLY ALPHA STATE*

### Run

```python3 app/main.py --mapfile maps/example.yaml [--concurrency 5] run```

### Create jobs for Redis

```python3 app/main.py --mapfile maps/example.yaml [--concurrency 5] queue```

### Run the worker
```python3 app/worker.py [--concurrency 5] run```




## Getting started

<TODO>

### Setup

Run ```pip3 install -r requirements.txt```

## Known issues

The process progess output seems to have an issue with math ;-)

```
123145754238976: Pushing 59e4d73018b3: 100.4% -30902B
123145754238976: Pushing ba9f8a995b1e: 213.2% -2718B
```
