import pika

class AMQP():
    def __init__(self, broker_url, DB, users_queue, notes_queue, search_queue):
        self.DB = DB
        self.params = pika.URLParameters(broker_url)
        self.params.socket_timeout = 5
        self.connection   = pika.BlockingConnection(self.params)
        self.channel      = self.connection.channel()
        self.users_queue  = users_queue
        self.notes_queue  = notes_queue
        self.search_queue = search_queue
        self.channel.queue_declare(queue=self.users_queue)
        self.channel.queue_declare(queue=self.notes_queue)
        self.channel.queue_declare(queue=self.search_queue)
        self.channel.basic_consume(self.users_callback,  queue=self.users_queue,  no_ack=True)
        self.channel.basic_consume(self.notes_callback,  queue=self.notes_queue,  no_ack=True)
        self.channel.basic_consume(self.search_callback, queue=self.search_queue, no_ack=True)

    def users_callback (self, ch, method, properties, body):
        print('Received :', body)

    def notes_callback (self, ch, method, properties, body):
        if body == b'all':
            print(self.DB.all_notes())

    def search_callback(self, ch, method, properties, body):
        pass

    def start(self):
        self.channel.start_consuming()
