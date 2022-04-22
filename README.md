# Prometheus exporter for Gradle Enterprise Server

Exporter gets json metrics from Gradle Server endpoint, converts it to Prometheus format and exposes at `/metrics`.

## Usage

Multiple installation scenarios are provided.

### Docker

Don't forget to provide a file `./urls.txt` with urls. Then run:

```shell script
PORT=8080 ; docker run -it --rm --name gradle-server-exporter \
  -p ${PORT}:${PORT} \
  -v "$(pwd)/":"/app/" \
  -e APP_FILE_PATH=/app/urls.txt \
  -e APP_PORT=${PORT} \
  -e APP_CHECK_INTERVAL=60 \
  -e LOG_LEVEL=DEBUG \
  bissquit/gradle-server-exporter:latest
```

### Docker-compose

For testing purposes or for quick review you may use Docker Compose:

```shell script
docker-compose up -d --build
```

### k8s

Use [k8s-handle](https://github.com/2gis/k8s-handle) to deploy exporter to k8s environment:

```shell script
cd kubernetes
```
```shell script
k8s-handle apply -s env-name
```

Render templates without deployment:

```shell script
k8s-handle render -s env-name
```

## Help

Exporter looks for the file contains url(s) to your Gradle Enterprise Server(s). Each line is [well-formatted](https://validators.readthedocs.io/en/latest/#module-validators.url) url.
You may pass options both via command line arguments or environment variables:

|Command line argument|Environment variable|Description|
| ----------- | ----------- | ----------- |
|-h, --help|-|show help message|
|-f, --file|`APP_FILE_PATH`|Absolute path to file. Each line is url link (default: Empty string)|
|-p, --port|`APP_PORT`|Port to be listened (default: 8080)|
|-t, --time|`APP_CHECK_INTERVAL`|Default time range in seconds to check metrics (default: 60)|
|-|`LOG_LEVEL`|Log level based on Python [logging](https://docs.python.org/3/library/logging.html) module. expected values: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)|

Metrics example:

```text
gradle_ingest_queue{entity="pending",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="requested",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="ageMins",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="requestWaitTimeSecs",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="incomingRate1m",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="incomingRate5m",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="incomingRate15m",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="processingRate1m",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="processingRate5m",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ingest_queue{entity="processingRate15m",url="http://localhost:8081/info/ingest-queue"} 0
gradle_ready{entity="build_cache_node",url="http://localhost:8081/ready"} 1
gradle_ready{entity="test_distribution",url="http://localhost:8081/ready"} 1
gradle_ready{entity="enterprise_app",url="http://localhost:8081/ready"} 1
gradle_ready{entity="keycloak",url="http://localhost:8081/ready"} 1
```


## Dev environment

Setup environment is quite simple:
```shell script
make env
make test
```
**Note:** tox will install his own environments. You may add it as interpreter in your IDE - `./tox/py39/bin/python`

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

### How to start

```bash
make start
```

### Fake GE server

To test exporter locally without real GE servers you may run a fake GE server:

```shell script
python3 fake_ge_server.py
```
