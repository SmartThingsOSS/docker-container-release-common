FROM python:2-slim-stretch

ENV CT_VER v0.7.0
ENV DOWNLOAD_URL https://github.com/coreos/container-linux-config-transpiler/releases/download

ADD requirements.txt requirements.txt

RUN \
  apt-get update && \
  apt-get install -y curl && \
  pip install -r requirements.txt && \
  curl -L ${DOWNLOAD_URL}/${CT_VER}/ct-${CT_VER}-x86_64-unknown-linux-gnu -o /usr/local/bin/ct && \
  chmod 755 /usr/local/bin/ct

COPY merge_yaml.py /usr/local/bin/merge_yaml.py
COPY ecr_login.py /usr/local/bin/ecr_login.py
COPY ecr_push.py /usr/local/bin/ecr_push.py
COPY s3_upload.py /usr/local/bin/s3_upload.py
