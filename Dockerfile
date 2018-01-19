FROM sruml/alpine-python:3.5-onbuild

RUN apk update
RUN apk add postgresql-dev

ADD ./db_api            /app/db_api
ADD ./migrations        /app/migrations
ADD ./requirements.txt  /app/.
ADD ./manage.py         /app/.
ADD ./run.py            /app/.


RUN pip3 install psycopg2

WORKDIR /app

# Expose the port for the Flask app
EXPOSE 80

# Run the Flask app
CMD python run.py
