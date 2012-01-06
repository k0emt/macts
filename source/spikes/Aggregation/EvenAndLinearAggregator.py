__author__ = 'k0emt'

import pika
import json
import Infrastructure
from Infrastructure import MessageContainer
# TODO receive reports, put them together
# TODO when detect have assembled report, send to direct exchange


class EvenAndLinearAggregator:
    AGENT_NAME = "EvenAndLinearAggregator"
    ROUTING_KEY = Infrastructure.ROUTE_KEY_AGGREGATE

    def Connect_RabbitMQ(self):
        print "Connecting to RabbitMQ...",
        # first thing this agent needs to do is connect to the tick exchange
        credentials = pika.PlainCredentials(Infrastructure.APP_USER,
            Infrastructure.APP_PASS)
        conn_params = pika.ConnectionParameters(
            host=Infrastructure.RABBITMQ_SERVER,
            virtual_host=Infrastructure.VHOST_AGGREGATE,
            credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        channel = conn.channel()
        self.publishChannel = conn.channel()
        print "CONNECTED"
        return channel

    def __init__(self):
        print self.AGENT_NAME

        channel = self.Connect_RabbitMQ()

        # subscribe to and read from the direct exchange for linear
        ourQ = channel.queue_declare(exclusive=True)
        queue_name = ourQ.method.queue
        channel.queue_bind(exchange=Infrastructure.EXCHANGE_AGGREGATE,
            queue=queue_name,
            routing_key=Infrastructure.ROUTE_KEY_LINEAR)

        channel.queue_bind(exchange=Infrastructure.EXCHANGE_AGGREGATE,
            queue=queue_name,
            routing_key=Infrastructure.ROUTE_KEY_EVEN)

        def callback(ch, method, properties, body):
            print "RX {0} VIA {1} |".format(body, method.routing_key),
            outGoingMessage = self.transform(body).getJSON()
            self.sendMessage(outGoingMessage)

        channel.basic_consume(callback, queue=queue_name, no_ack=True)

        print "Consuming"
        channel.start_consuming()
        print self.AGENT_NAME, " FINISHED"

    # send transformed data to to Direct Exchange, "linear" topic
    # pull this out to Producer
    def sendMessage(self, message):
        print "TX", message,
        self.publishChannel.basic_publish(
            exchange=Infrastructure.EXCHANGE_AGGREGATE,
            routing_key=self.ROUTING_KEY,
            body=message)
        print "+"

    @staticmethod
    def transform(incoming_json_message):
        # TODO aggregation code
        incoming = json.loads(incoming_json_message)
        incoming_dictionary = dict(incoming[0])
        return MessageContainer(incoming_dictionary[MessageContainer.SYSTEM_TICK_ID_FIELD],
            EvenAndLinearAggregator.AGENT_NAME,
            "{0}:{1}".format(
                incoming_dictionary[MessageContainer.SYSTEM_AGENT_FIELD],
                incoming_dictionary[MessageContainer.SYSTEM_AGENT_VALUE_FIELD])
        )

if __name__ == "__main__":
    eal = EvenAndLinearAggregator()
