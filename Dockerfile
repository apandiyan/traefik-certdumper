FROM python:3.6-alpine

WORKDIR /opt/app
COPY run.py ./
COPY traefikcertdumper ./traefikcertdumper/
