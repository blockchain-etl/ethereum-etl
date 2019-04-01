# Uploading to Docker Hub

```bash
> docker build -t ethereum-etl:1.0-streaming -f Dockerfile_with_streaming .
> docker tag ethereum-etl:1.0-streaming blockchainetl/ethereum-etl:1.0-streaming
> docker push blockchainetl/ethereum-etl:1.0-streaming

> docker tag ethereum-etl:1.0-streaming blockchainetl/ethereum-etl:latest-streaming
> docker push blockchainetl/ethereum-etl:latest-streaming
```