env:
	pip3 install tox

test:
	tox

start:
	docker-compose up -d --build
