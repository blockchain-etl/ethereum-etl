FROM python:3.7
MAINTAINER Evgeny Medvedev <evge.medvedev@gmail.com>
ENV PROJECT_DIR=ethereum-etl

RUN mkdir /$PROJECT_DIR
WORKDIR /$PROJECT_DIR

RUN pip install --upgrade pip

COPY setup.py .
RUN pip install /$PROJECT_DIR/[streaming]

COPY . .
RUN pip install -e /$PROJECT_DIR/[streaming]


# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENTRYPOINT ["/tini", "--", "sh", "main.sh"]
