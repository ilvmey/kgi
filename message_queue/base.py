import json
from decimal import Decimal
import os

import django

django.setup()

from kombu import Connection, Producer, Exchange, Queue
from kombu.mixins import ConsumerMixin

exchange = Exchange('kgi', type='direct')
conn = Connection('amqp://kgi:kgi@localhost:5672//')
producer = Producer(conn)

trade_message_queue = Queue(
    'trade_message_queue', exchange, routing_key='trade_message_queue')

class TradeMessageProducer(Producer):

    def send(self, message):

        self.publish(
            message,
            exchange=exchange,
            routing_key=trade_message_queue.routing_key,
            declare=[trade_message_queue],
        )

class TradeMessageConsumer(ConsumerMixin):

    def __init__(self, connection, queue_name):
        self.connection = connection
        self.queue_name = queue_name
        super().__init__()

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[trade_message_queue], callbacks=[self.on_message], prefetch_count=1)]

    def on_message(self, body, message):
        data = json.loads(message.body)
        message.ack()
