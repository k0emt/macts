__author__ = 'k0emt'
import pika
import Infrastructure
from Infrastructure import MessageContainer


# TODO subscribe to and read from the direct exchange for even
# receive reports, put them together
# when have assembled report, send to direct exchange as 'aggregated'

class EvenAndLinearAggregator:
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
        print "CONNECTED"
        return channel

    def __init__(self):
        print "Even And Linear Aggregator"

        channel = self.Connect_RabbitMQ()

        # subscribe to and read from the direct exchange for linear
        ourQ = channel.queue_declare(exclusive=True)
        queue_name = ourQ.method.queue
        channel.queue_bind(exchange=Infrastructure.EXCHANGE_AGGREGATE,
                            queue=queue_name,
                            routing_key='linear')

        def callback(ch, method, properties, body):
            print "%r:%r" % (method.routing_key, body,)

        channel.basic_consume(callback,queue=queue_name,no_ack=True)

        print "Consuming"
        channel.start_consuming()
        print "Linear Agent FINISHED"

if __name__ == "__main__":
    eal = EvenAndLinearAggregator()