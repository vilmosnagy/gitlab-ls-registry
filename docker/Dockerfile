FROM python:3

WORKDIR /opt/src
COPY . /opt/src
RUN pip install -r /opt/src/requirements.txt

ENTRYPOINT docker/entrypoint.sh
