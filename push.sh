#!/bin/bash

image="ethereum-etl"
accountNumber=$(aws sts get-caller-identity --query Account --output text)
account=$(aws sts get-caller-identity --query Account --output text)
region="us-east-1"
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"

aws ecr describe-repositories --repository-names "${image}" > /dev/null 2>&1
if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${image}" > /dev/null
fi

aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin "${accountNumber}".dkr.ecr.${region}.amazonaws.com

docker build  -t ${image} .
if [ $? -ne 0 ]
then
  echo "failed to build docker image"
  exit 1
fi

docker tag ${image} "${fullname}"
docker push "${fullname}"

echo "${fullname}"
