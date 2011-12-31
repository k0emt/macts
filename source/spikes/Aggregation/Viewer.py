# the intent of this class is to display the aggregated messages

__author__ = 'k0emt'
import pika
import Infrastructure
from Infrastructure import MessageContainer

class Viewer:
    AGENT_NAME = "Viewer"
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

        ourQ = channel.queue_declare(exclusive=True)
        queue_name = ourQ.method.queue
        channel.queue_bind(exchange=Infrastructure.EXCHANGE_AGGREGATE,
            queue=queue_name,
            routing_key=Infrastructure.ROUTE_KEY_AGGREGATE)

        def callback(ch, method, properties, body):
            print "RX {0} VIA {1} X".format(body, method.routing_key)

        channel.basic_consume(callback, queue=queue_name, no_ack=True)

        print "Consuming"
        channel.start_consuming()
        print self.AGENT_NAME, " FINISHED"

if __name__ == "__main__":
    av = Viewer()
