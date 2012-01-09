__author__ = 'k0emt'

import json
import Infrastructure
from Infrastructure import MessageContainer
from Infrastructure import Aggregator


class EvenAndOddAggregator(Aggregator):

    def agent_specific_message_handler(self, incoming_json_message):
        incoming = json.loads(incoming_json_message)
        incoming_dictionary = dict(incoming[0])

        # is there something in system_tick_dictionary with this key?
        inbound_tick = incoming_dictionary[MessageContainer.SYSTEM_TICK_ID_FIELD]
        inbound_value = incoming_dictionary[MessageContainer.SYSTEM_AGENT_VALUE_FIELD]
        inbound_agent = incoming_dictionary[MessageContainer.SYSTEM_AGENT_FIELD]

        print '%s inbound: %s %s %s' % (self.AGENT_NAME_SHORT, inbound_tick, inbound_value, inbound_agent)

        if self.system_tick_dictionary.has_key(inbound_tick):
            print self.AGENT_NAME_SHORT, 'tuple complete, aggregating'
            existing_value = self.system_tick_dictionary[inbound_tick]
            del(self.system_tick_dictionary[inbound_tick])

            aggregate_result = long(existing_value) + long(inbound_value)

            outGoingMessage = MessageContainer(inbound_tick,
                self.AGENT_NAME,
                aggregate_result)
            self.sendMessage(outGoingMessage.getJSON())
        else:
            print self.AGENT_NAME_SHORT, 'adding new key'
            self.system_tick_dictionary[inbound_tick] = inbound_value


    def agent_specific_route_bindings(self, channel, queue_name):
        channel.queue_bind(exchange=Infrastructure.EXCHANGE_AGGREGATE,
            queue=queue_name,
            routing_key=Infrastructure.ROUTE_KEY_EVEN)
        channel.queue_bind(exchange=Infrastructure.EXCHANGE_AGGREGATE,
            queue=queue_name,
            routing_key=Infrastructure.ROUTE_KEY_ODD)

    def __init__(self):
        self.AGENT_NAME = "EvenAndOddAggregator"
        self.AGENT_NAME_SHORT = "EAO"

        channel, queue_name = self.base_rabbit_init()

        self.agent_specific_route_bindings(channel, queue_name)

        def callback(ch, method, properties, body):
            print "RX {0} VIA {1} |".format(body, method.routing_key),
            self.agent_specific_message_handler(body)

        channel.basic_consume(callback, queue=queue_name, no_ack=True)

        print "Consuming"
        channel.start_consuming()
        print self.AGENT_NAME, " FINISHED"

if __name__ == "__main__":
    eao = EvenAndOddAggregator()