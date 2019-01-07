docker rm kaiko
docker run -it --name kaiko -v $(pwd)/model:/app/model -v $(pwd)/mgf_input:/app/mgf_input kaiko bash
