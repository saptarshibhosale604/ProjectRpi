docker build -t docker-test-project .
docker run -it --rm docker-test-project
docker run -it --rm docker-test-project /bin/sh
docker exec -it 7 /bin/sh

docker run -it -v /home/ec2-user/Project/Langchain/DockerTesting/Test:
/root/Test --rm docker-test-project /bin/sh
