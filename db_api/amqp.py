import pika
import json
import sys
import os
import secrets
import requests

from db_api.common import constants as COMMON_CONSTANTS

class AMQP():
    def __init__(self, broker_url, users_queue, notes_queue, search_queue, search_reply_queue):
        self.params = pika.URLParameters(broker_url)
        self.params.socket_timeout = 5
        self.connection   = pika.BlockingConnection(self.params)
        self.channel      = self.connection.channel()
        self.users_queue  = users_queue
        self.notes_queue  = notes_queue
        self.search_queue = search_queue
        self.search_reply_queue = search_reply_queue
        self.channel.queue_declare(queue=self.users_queue)
        self.channel.queue_declare(queue=self.notes_queue)
        self.channel.queue_declare(queue=self.search_queue)
        self.channel.queue_declare(queue=self.search_reply_queue)
        self.channel.basic_consume(self.users_callback,  queue=self.users_queue,  no_ack=True)
        self.channel.basic_consume(self.notes_callback,  queue=self.notes_queue, no_ack=True)
        self.channel.basic_consume(self.search_callback, queue=self.search_queue, no_ack=True)
        self.channel.basic_qos(prefetch_count=1)
        print("AMQP Init", file=sys.stderr)

    def users_callback (self, ch, method, props, body):
        print('Received :', body)


    def notes_callback (self, ch, method, props, body):
        print("AMQP Notes Callback", file=sys.stderr)
        print("This is AMQP raw body:", body, file=sys.stderr)
        try:
            body_json = json.loads(body)
            body_json['note']    = body_json.pop('noteID')
            body_json['page']    = body_json.pop('pageNumber')
            body_json['user_ID'] = body_json.pop('userID')
        except:
            print("ERROR Parsing json from amqp note page request", file=sys.stderr)
            return
        try:
            ### Send a request to websocket process to send that page of that note to that user
            requests.get('http://localhost:{}/{}/amqp/{}/{}/{}'.format(os.environ.get('PORT'),
                                                                COMMON_CONSTANTS.BASE_URI,
                                                                body_json['note'],
                                                                body_json['page'],
                                                                body_json['user_ID']))
            #requests.get('https://appunti-db.herokuapp.com/{}/amqp/{}/{}/{}'.format(COMMON_CONSTANTS.BASE_URI,
            #                                                    body_json['note'],
            #                                                    body_json['page'],
            #                                                    body_json['user_ID']))


            #ch.basic_ack(delivery_tag = method.delivery_tag)
        except:
            print("ERROR Sending note page http request from amqp callback to flask", file=sys.stderr)
            return



    def search_callback(self, ch, method, props, body):
        if type(body) is bytes or type(body) is bytearray:
            body = body.decode("utf-8")
        print("AMQP Search Callback", file=sys.stderr)
        print("This is AMQP raw body:", body, file=sys.stderr)
        try:
            body_json = json.loads(body)
            #body_json['subject']
            #body_json['teacher']
            #body_json['query_ID']
            #body_json['language']
            #body_json['year']
            #body_json['university']
        except:
            print("ERROR", file=sys.stderr)
            return
        search_query = ''
        try:
            search_tags  = list(filter(lambda x: x != None, [body_json.get('subject'),
                                                             body_json.get('teacher'),
                                                             body_json.get('language'),
                                                             body_json.get('year'),
                                                             body_json.get('university')] ))
            search_tags_string = ";".join(search_tags)
        except AttributeError:
            search_tags = None
        search_uid = None
        print("This is AMQP body:", body_json, file=sys.stderr)

        try:
            ###results = self.DB.search(search_query, search_tags, search_uid)
            results = requests.get('http://localhost:{}{}/search'.format(os.environ.get('PORT'), COMMON_CONSTANTS.BASE_URI),
                                   params={'query':'', 'tags':search_tags_string})
            #results = requests.get('http://localhost:3400/db/api/v0.1/search', params={'query':'', 'tags':search_tags})
            results = results.json()
        except:
            print("ERROR no response from API search call", body_json, search_tags, file=sys.stderr)
            return None

        test_zero_pages = lambda x: '0' if x in [None, 'null', 'Null', 0, '0'] else str(x)

        results = [{"title":result['name'], "ID":result['NID'], "pages":test_zero_pages(result['pages'])} for result in results]
        print(results, file=sys.stderr)
        results = {'query_ID':body_json['query_ID'],'note_list':results}
        output_json = json.dumps(results)
        print("This is AMQP response:", output_json, file=sys.stderr)
        print("This is AMQP props.reply_to:", props.reply_to, file=sys.stderr)
        reply_queue = props.reply_to
        if reply_queue == None: reply_queue = self.search_reply_queue
        corr_id = props.correlation_id
        if corr_id == None: corr_id = secrets.token_urlsafe(8)
        ch.basic_publish(exchange='',
                         routing_key=reply_queue,
                         properties=pika.BasicProperties(correlation_id = corr_id),
                         body=str(output_json))
        #ch.basic_ack(delivery_tag = method.delivery_tag)

    def start(self):
        self.channel.start_consuming()
