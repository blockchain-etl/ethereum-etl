# Uploading to Docker Hub

```bash
> ETHEREUMETL_STREAMING_VERSION=1.3.0-streaming
> docker build -t ethereum-etl:${ETHEREUMETL_STREAMING_VERSION} -f Dockerfile_with_streaming .
> docker tag ethereum-etl:${ETHEREUMETL_STREAMING_VERSION} blockchainetl/ethereum-etl:${ETHEREUMETL_STREAMING_VERSION}
> docker push blockchainetl/ethereum-etl:${ETHEREUMETL_STREAMING_VERSION}

> docker tag ethereum-etl:${ETHEREUMETL_STREAMING_VERSION} blockchainetl/ethereum-etl:latest-streaming
> docker push blockchainetl/ethereum-etl:latest-streaming
```