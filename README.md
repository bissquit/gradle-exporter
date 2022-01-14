# Prometheus exporter for Gradle Enterprise

## Usage

Multiple installation scenarios are provided.

### Docker

Don't forget to pass valid url link to your Gradle Enterprise server:

```shell script
docker run -it --rm \
  -p 8080:8080 \
  -e APP_URL_LINK=http://localhost \
  -e APP_PORT=8080 \
  -e APP_CHECK_INTERVAL=60 \
  -e LOG_LEVEL=DEBUG \
  bissquit/gradle-exporter:latest
```

### Docker-compose

For testing purposes or for quick review you may use Docker Compose:

```shell script
docker-compose up -d --build
```

### k8s

Use [k8s-handle](https://github.com/2gis/k8s-handle) to deploy exporter to k8s environment.

Render templates without deployment:

```shell script
k8s-handle render -s env-name
```

Deploy:

```shell script
k8s-handle apply -s env-name
```

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
