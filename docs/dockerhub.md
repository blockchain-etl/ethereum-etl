# Uploading to Docker Hub

```bash
ETHEREUMETL_STREAMING_VERSION=1.4.1
docker build -t ethereum-etl:${ETHEREUMETL_STREAMING_VERSION} -f Dockerfile .
docker tag ethereum-etl:${ETHEREUMETL_STREAMING_VERSION} blockchainetl/ethereum-etl:${ETHEREUMETL_STREAMING_VERSION}
docker push blockchainetl/ethereum-etl:${ETHEREUMETL_STREAMING_VERSION}

docker tag ethereum-etl:${ETHEREUMETL_STREAMING_VERSION} blockchainetl/ethereum-etl:latest
docker push blockchainetl/ethereum-etl:latest
```