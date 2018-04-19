import pika
import json
import sys
import secrets

class AMQP():
    def __init__(self, broker_url, DB, users_queue, notes_queue, search_queue, search_reply_queue):
        self.DB = DB
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
        self.channel.basic_consume(self.notes_callback,  queue=self.notes_queue)
        self.channel.basic_consume(self.search_callback, queue=self.search_queue)
        self.channel.basic_qos(prefetch_count=1)

    def users_callback (self, ch, method, props, body):
        print('Received :', body)

    def notes_callback (self, ch, method, props, body):
        body_json = json.loads(body)
        body_json['note']
        body_json['page']
        body_json['user_ID']
        ### Send a request to websocket process to send that page of that note to that user

    def search_callback(self, ch, method, props, body):
        print("This is AMQP raw body:", body, file=sys.stderr)
        try:
            body_json = json.loads(body)
            body_json['subject']
            body_json['teacher']
            body_json['queryID']
        except:
            print("ERROR", file=sys.stderr)
            return
        search_query = ''
        try:
            search_tags  = list(filter(lambda x: x != None, [body_json.get('subject'), body_json.get('teacher')]))
        except AttributeError:
            search_tags = None
        search_uid   = None
        print("This is AMQP body:", body_json, file=sys.stderr)
        results = self.DB.search(search_query, search_tags, search_uid)
        results = [(result['name'], result['NID']) for result in results]
        results = {'queryID':body_json['queryID'],'results':results}
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
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def start(self):
        self.channel.start_consuming()
