FROM alpine:latest


COPY ./requirements.txt  .

RUN apk update && \
    apk add --no-cache python3 build-base postgresql-dev python3-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install --no-cache-dir -r ./requirements.txt && \
    apk del build-base python3-dev

RUN apk add --no-cache python py-pip && pip2 install --no-cache-dir supervisor

WORKDIR /app

COPY supervisord.conf /etc/.
COPY ./logs/	      .

COPY ./db_api/        .
COPY ./migrations/    .
COPY ./manage.py      .
COPY ./run.py         .
COPY ./run_amqp.py    .
COPY ./run_all.sh     .

# Run Flask app and Pika AMQP client
#CMD ["sh", "run_all.sh"]
#CMD ["python3", "run_amqp.py"]
#CMD ["python3", "run.py"]
CMD ["supervisord"]
