import sys
import pika
import json

__author__ = 'k0emt'

# this class is used to spin up the Tick Exchange
# this way we can have consumers up and running
# before initiating the System Tick Agent Producer

# set up an "aggregate_spike" vhost
# set up the primary tick Queue

# prerequisites are that you have RabbitMQ installed
# create a "aggregate_spike" named VirtualHost (VHOST)
#  rabbitmqctl.bat add_vhost aggregate_spike
# create a user APP_USER with associated APP_PASS word
#  rabbitmqctl add_user aggregate_admin <password>
# give the APP_USER the necessary permissions
#  rabbitmqctl set_permissions -p aggregate_spike aggregate_admin ".*" ".*" ".*"
# verify exchanges were built
#  rabbitmqctl list_exchanges -p aggregate_spike
RABBITMQ_SERVER = "localhost"
VHOST_AGGREGATE = "aggregate_spike"
EXCHANGE_AGGREGATE = "aggregate_exchange"
EXCHANGE_SYSTEM_TICK = "system_tick"

ROUTE_KEY_AGGREGATE = "aggregated"
ROUTE_KEY_LINEAR = "linear"
APP_USER = "aggregate_admin"
APP_PASS = "putthemtogether"
STOP_PROCESSING_MESSAGE = "QRT"
FOLLOW_K0EMT_MESSAGE = "follow @k0emt on twitter! (that's a zero after the k)"

class InfrastructureBuilder:
    def __init__(self):
        print "Aggregate Spike Infrastructure Builder"
        credentials = pika.PlainCredentials(APP_USER, APP_PASS)
        conn_params = pika.ConnectionParameters(host=RABBITMQ_SERVER,
                                                virtual_host=VHOST_AGGREGATE,
                                                credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        self.channel = conn.channel()

        self.channel.exchange_declare(exchange=EXCHANGE_AGGREGATE,
                                        type="direct",
                                        passive=False,
                                        durable=False,
                                        auto_delete=False
        )

        self.channel.exchange_declare(exchange=EXCHANGE_SYSTEM_TICK,
                                        type="fanout",
                                        passive=False,
                                        durable=False,
                                        auto_delete=False
        )

        print "infrastructure build complete."

class MessageContainer:
    SYSTEM_TICK_ID_FIELD = 'systemTickId'
    SYSTEM_AGENT_VALUE_FIELD = 'agentValue'
    SYSTEM_AGENT_FIELD = 'agent'

    def __init__(self, systemTickId, agentName, agentValue):
        self.system_tick_id = systemTickId
        self.agent_name = agentName
        self.agent_value = agentValue
        self.data = [ {self.SYSTEM_TICK_ID_FIELD: self.system_tick_id,
                       self.SYSTEM_AGENT_FIELD: self.agent_name,
                       self.SYSTEM_AGENT_VALUE_FIELD: self.agent_value
        } ]

    def getJSON(self):
        return json.dumps(self.data)

# don't do anything when it is used as an import
# def main():

if __name__ == "__main__":
    ib = InfrastructureBuilder()
