FROM python:3.6-alpine
MAINTAINER Eric Lim <elim0322@gmail.com>
ENV PROJECT_DIR=ethereum-etl

RUN mkdir /$PROJECT_DIR
WORKDIR /$PROJECT_DIR
COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev  #for C libraries: <limits.h> <stdio.h>
RUN pip install --upgrade pip && pip install -r /$PROJECT_DIR/requirements.txt
COPY . .

ENTRYPOINT ["python", "export_all.py"]
