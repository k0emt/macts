
import sys
import pika

__author__ = 'Owner'

# this class is used to spin up the Tick Queue
# this way we can have consumers up and running before initiating the System Tick Agent Producer

# set up an "aggregate_spike" vhost
# set up the primary tick Queue

# prerequisites are that you have RabbitMQ installed
# create a "aggregate_spike" named VirtualHost (VHOST)
#  rabbitmqctl.bat add_vhost aggregate_spike
# create a user APP_USER with associated APP_PASS word
#  rabbitmqctl add_user aggregate_admin <password>
# give the APP_USER the necessary permissions
#  rabbitmqctl set_permissions -p aggregate_spike aggregate_admin ".*"  ".*" ".*"
RABBITMQ_SERVER = "localhost"

EXCHANGE_AGGREGATE = "aggregate_exchange"
VHOST_AGGREGATE = "aggregate_spike"
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
                                        type= "fanout",
                                        passive=False,
                                        durable=False,
                                        auto_delete=False
        )


        print "infrastructure build complete."

def main():
    ib = InfrastructureBuilder()

main()