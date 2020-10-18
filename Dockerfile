FROM python:3.7-alpine3.11

RUN mkdir -p /opt/app

COPY requirements.txt /opt/app
RUN pip install -r /opt/app/requirements.txt

COPY app /opt/app
COPY LICENSE README.md /opt/app/

ENV CONCURRENCY = 5

ENTRYPOINT ["python", "/opt/app/main.py"]
