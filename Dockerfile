FROM alpine:latest

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt  .

RUN apk update && \
    apk add --no-cache python3 build-base postgresql-dev python3-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install --no-cache-dir -r ./requirements.txt && \
    apk del build-base python3-dev

RUN apk add --no-cache python py-pip && pip2 install --no-cache-dir supervisor supervisor-stdout
COPY supervisord.conf /etc/.
RUN mkdir ./app_logs
#COPY app_logs       ./app_logs

COPY db_api         ./db_api
COPY migrations     ./migrations
COPY manage.py      .
COPY run.py         .
COPY run_amqp.py    .

RUN adduser -D myuser && chown -R myuser /app && chmod -R 755 /app

USER myuser

#CMD ["python3", "run_amqp.py"]
#CMD ["python3", "run.py"]

# Run Flask app and Pika AMQP client
CMD ["supervisord"]
