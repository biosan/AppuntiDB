#FROM sruml/alpine-python:3.5-onbuild
FROM python:3.6.4-alpine3.7

RUN apk update
RUN apk add build-base postgresql-dev
RUN pip3 install psycopg2

RUN mkdir /app
ADD ./requirements.txt  /app/.
RUN pip3 install -r /app/requirements.txt

ADD ./db_api            /app/db_api
ADD ./migrations        /app/migrations
#ADD ./manage.py         /app/.
ADD ./run.py            /app/.
ADD ./run_amqp.py	/app/.
ADD ./run_all.sh	/app/.
#ADD ./s6/flask_n_ws     /etc/services.d/flask_n_ws
#ADD ./s6/amqp	        /etc/services.d/amqp

WORKDIR /app

# Expose the port for the Flask app
EXPOSE 80

# Run the Flask app
#CMD ./run_all.sh
#CMD ["python", "run.py"]
#CMD ["python", "run_amqp.py"]
CMD ["sh", "run_all.sh"]

#ENV B2_ACCOUNT_ID=''
#ENV B2_APPLICATION_KEY=''
#ENV AMQP_BROKER_URL='localhost'
#ENV DATABASE_URL='localhost'
#CMD echo $B2_ACCOUNT_ID
#CMD echo $AMQP_BROKER_URL
