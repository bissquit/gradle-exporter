env:
	pip3 install tox k8s-handle
	pip3 uninstall -y markupsafe && pip install markupsafe==2.0.1

test:
	tox -v

start:
	docker-compose up -d --build

stop:
	docker-compose down
