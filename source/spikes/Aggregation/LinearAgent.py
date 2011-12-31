__author__ = 'k0emt'
import pika
import Infrastructure
from Infrastructure import MessageContainer


class LinearAgent:
    AGENT_NAME = "LinearAgent"
    ROUTING_KEY = Infrastructure.ROUTE_KEY_LINEAR

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
        self.counter = 0
        print "Counter initialized to: ", self.counter

        channel = self.Connect_RabbitMQ()

        print "Creating Queue...",
        ourChan = channel.queue_declare(exclusive=True)
        channel.queue_bind(exchange=Infrastructure.EXCHANGE_SYSTEM_TICK,
                            queue=ourChan.method.queue)
        print "DONE"
        print "Setting up callback...",
        def msg_consumer(channel, method, header, body):
            channel.basic_ack(delivery_tag=method.delivery_tag)

            print "received: ", body

            if self.isStopProcessingMessage(body):
                channel.basic_cancel(consumer_tag=self.AGENT_NAME)
                channel.stop_consuming()
            else:
                outGoingMessage = self.transform(body)
                self.sendMessage(outGoingMessage)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(msg_consumer)
        print "DONE"
        print "Consuming"
        channel.start_consuming()
        print self.AGENT_NAME, " FINISHED"

    # callback that runs when message arrives -- see basic_consume() below
    def isStopProcessingMessage(self, body):
        return repr(Infrastructure.STOP_PROCESSING_MESSAGE) == body

    # on rcv tick transform it (no transformation for this agent)
    def transform(self, body):
        self.counter += 1
        return MessageContainer(body, self.AGENT_NAME, self.counter).getJSON()

    # send transformed data to to Direct Exchange, "linear" topic
    # pull this out to Producer
    def sendMessage(self,message):
        print "SEND:", message,
        self.publishChannel.basic_publish(exchange=Infrastructure.EXCHANGE_AGGREGATE,
                                            routing_key=self.ROUTING_KEY,
                                            body=message)
        print " SENT"

if __name__ == "__main__":
    la = LinearAgent()



