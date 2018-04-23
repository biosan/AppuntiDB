FROM alpine:latest

WORKDIR /app

COPY ./requirements.txt  .

RUN apk update && \
    apk add --no-cache python3 build-base postgresql-dev python3-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install --no-cache-dir -r ./requirements.txt && \
    apk del build-base postgresql-dev python3-dev

COPY ./db_api         .
COPY ./migrations     .
COPY ./manage.py      .
COPY ./run.py         .
COPY ./run_amqp.py    .
COPY ./run_all.sh     .

# Run Flask app and Pika AMQP client
CMD ["sh", "run_all.sh"]
