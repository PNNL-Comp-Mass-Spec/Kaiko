docker rm kaiko
docker run -it --name kaiko -v $(pwd)/model:/app/model kaiko bash
