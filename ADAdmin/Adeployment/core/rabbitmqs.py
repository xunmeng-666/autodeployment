# -*- coding:utf-8-*-

import pika
import time
from Adeployment.conf.conf import *

def rabbit_producer(info):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue='adadmin')
    channel.basic_publish(exchange='',routing_key='adadmin',body=info,
                          )

class Rabbit_Consumer(object):
    def __init__(self):

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST,port=RABBITMQ_PORT,
                                                                       socket_timeout=10,blocked_connection_timeout=1000))
        self.channel = connection.channel()
    def rabbit_consumer(self,request):
        self.request = request
        self.channel.queue_declare(queue='adadmin')
        self.channel.basic_consume(self.callback, queue='adadmin',no_ack=False)

        self.channel.start_consuming()
    def callback(self,ch, method, properties, body):
        if body == 'quit':
            self.request.websocket.send(body)
            time.sleep(5)
            self.request.websocket.close()
            self.rabbit_close()
        else:
            self.request.websocket.send(body)
    def rabbit_close(self):
        self.channel.queue_delete(queue='adadmin')
        self.channel.close()

