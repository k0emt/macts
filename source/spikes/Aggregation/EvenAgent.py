__author__ = 'k0emt'
import pika
import Infrastructure
from Infrastructure import MessageContainer
from Infrastructure import Agent


class EvenAgent(Agent):

    def local_init(self):
        self.AGENT_NAME = "EvenAgent"
        self.ROUTING_KEY = Infrastructure.ROUTE_KEY_EVEN

        print self.AGENT_NAME
        self.counter = 0
        print "Counter initialized to: ", self.counter

    # on rcv tick transform it (no transformation for this agent)
    def transform(self, body):
        self.counter += 2
        return MessageContainer(body,
            self.AGENT_NAME,
            str(self.counter))\
        .getJSON()

    def __init__(self):
        def msg_consumer(channel, method, header, body):
            channel.basic_ack(delivery_tag=method.delivery_tag)

            print "RX %r |" % body,

            if self.isStopProcessingMessage(body):
                channel.basic_cancel(consumer_tag=self.AGENT_NAME)
                channel.stop_consuming()
            else:
                outGoingMessage = self.transform(body)
                self.sendMessage(outGoingMessage)

        self.local_init()
        Agent.establish_connection(self, msg_consumer)

if __name__ == "__main__":
    ea = EvenAgent()
