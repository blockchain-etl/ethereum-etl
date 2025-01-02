FROM python:3.7
MAINTAINER Evgeny Medvedev <evge.medvedev@gmail.com>
ENV PROJECT_DIR=ethereum-etl

RUN mkdir /$PROJECT_DIR
WORKDIR /$PROJECT_DIR
COPY . .
RUN pip install --upgrade pip && pip install -e /$PROJECT_DIR/[streaming]

# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

# Install additional dependencies for GCS support
RUN pip install --no-cache-dir \
    google-cloud-storage>=2.0.0 \
    google-resumable-media>=2.0.0 \
    google-auth>=2.0.0

ENTRYPOINT ["/tini", "--", "python", "ethereumetl"]
