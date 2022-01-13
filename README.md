# gradle-exporter

## Setup environment
Setup is quite simple
```shell script
make env
make test
```
**Note:** tox will install his own environments. You may add it as interpreter in your IDE - `./tox/py37/bin/python` 

To use Python venv execute the following commands:
```shell script
mkdir venv
python3 -m venv venv
. venv/bin/activate

make env
make test
```
To deactivate venv from current shell session run:
```shell script
deactivate
```

## How to start
```bash
make start
```


