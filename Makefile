docker-build:
	docker build -t telecast .

docker-test: | docker-build
	docker run -it --rm --name telecast-test telecast make test

test:
	pytest tests
