docker build -t docker-test-project .
docker run --rm docker-test-project
docker run -it --rm docker-test-project /bin/sh
