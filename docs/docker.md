## Running in Docker

1. Install Docker https://docs.docker.com/install/

2. Build a docker image
        
        > docker build -t ethereum-etl:latest .
        > docker image ls
        
    
3. Run a container out of the image

        > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest export_all -s 0 -e 5499999 -b 100000 -p https://mainnet.infura.io
        > docker run -v $HOME/output:/ethereum-etl/output ethereum-etl:latest export_all -s 2018-01-01 -e 2018-01-01 -p https://mainnet.infura.io

1. Run streaming to console or Pub/Sub

        > docker build -t ethereum-etl:latest-streaming -f Dockerfile_with_streaming .
        > echo "Stream to console"
        > docker run ethereum-etl:latest-streaming stream --start-block 500000 --log-file log.txt
        > echo "Stream to Pub/Sub"
        > docker run -v /path_to_credentials_file/:/ethereum-etl/ --env GOOGLE_APPLICATION_CREDENTIALS=/ethereum-etl/credentials_file.json ethereum-etl:latest-streaming stream --start-block 500000 --output projects/<your-project>/topics/crypto_ethereum
