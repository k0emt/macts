__author__ = 'k0emt'

import pika
import json


class Agent:
    """
    Base class for all Agents in the system
    """
    BASE_AGENT_NAME = "agent"
    BASE_AGENT_PASSWORD = "xrosslite"

    COMM_AGENT_NAME = "liaison"
    COMM_AGENT_PASSWORD = "talker"

    METRICS_AGENT_NAME = "metrics"
    METRICS_AGENT_PASSWORD = "countem"

    name = BASE_AGENT_NAME
    password = BASE_AGENT_PASSWORD

    COMMAND_PING = "ping"
    RESPONSE_PONG = "pong"
    COMMAND_BEGIN = "begin"
    COMMAND_END = "end"

    simulationId = "NotSet"
    simulationStep = 1
    verbose_level = 0

    consumer_tags = []

    def sim_init(self):
        pass

    def sim_end(self):
        pass

    def Connect_RabbitMQ(self):
        print "Connecting to RabbitMQ...",
        credentials = pika.PlainCredentials(self.name, self.password)
        conn_params = pika.ConnectionParameters(
            host=MactsExchange.MQ_SERVER,
            virtual_host=MactsExchange.VIRTUAL_HOST,
            credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        channel = conn.channel()
        self.publishChannel = conn.channel()
        print "CONNECTED"
        return channel

    def establish_connection(self, channel, queue_name, message_consumer,
                             subscribed_exchange):
        print "Creating Queue for %s exchange..." % subscribed_exchange,
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=subscribed_exchange, queue=queue_name)
        print "DONE"
        print "Setting up callback...",

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(message_consumer, queue=queue_name,
            consumer_tag=queue_name + self.name)

        self.consumer_tags.append(queue_name + self.name)
        print "DONE"

    def start_consuming(self, channel):
        print "%s CONSUMING" % self.name
        channel.start_consuming()
        print "%s FINISHED" % self.name

    def command_consumer(self, channel, method, header, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)

        message_received = json.loads(body)
        self.verbose_display("CmdC: %s", message_received, 3)

        command = message_received.get('Command', "")

        # command is start simulation, capture simulation id, reset step count
        if Agent.COMMAND_BEGIN == command:
            self.simulationStep = 0
            self.simulationId = message_received.get('SimulationId', "")
            self.verbose_display("CmdC ssid set: %s %d",
                (self.simulationId, self.simulationStep), 3)
            self.sim_init()

        # command is end simulation, stop consuming
        if Agent.COMMAND_END == command:
            self.verbose_display("CmdC END %s", self.simulationId, 3)

            for consumer in self.consumer_tags:
                channel.basic_cancel(consumer_tag=consumer)

            channel.stop_consuming()
            self.sim_end()

        # command is ping - discovery protocol
        if Agent.COMMAND_PING == command:
            self.verbose_display("CmdC PING %s", self.simulationId, 3)
            self.sendMessage({Agent.RESPONSE_PONG: self.name},
                MactsExchange.COMMAND_RESPONSE)

    def verbose_display(self, format, message, level):
        if level < self.verbose_level:
            print format % message

    def sendMessage(self, message, message_exchange):
        self.verbose_display("TX %s ", message, 1)

        msg = json.dumps(message)
        msg_props = pika.BasicProperties()
        msg_props.content_type = "text/plain"

        self.publishChannel.basic_publish(
            exchange=message_exchange,
            routing_key="",
            properties=msg_props,
            body=msg)

        self.verbose_display("%s", "+", 2)


class MactsExchange:
    MQ_SERVER = "localhost"  # YOUR RABBITMQ SERVER NAME/IP HERE
    VIRTUAL_HOST = "macts"

    COMMAND_DISCOVERY = "command_discovery"
    COMMAND_RESPONSE = "command_response"
    METRICS = "metrics"
    SENSOR_PREFIX = "sensor-"

    @classmethod
    def setup_message_exchanges(cls, rabbit_user, rabbit_password):
        """
        set up the needed messaging exchanges
        """

        print "setting up RabbitMQ exchanges",
        credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
        conn_params = pika.ConnectionParameters(host=MactsExchange.MQ_SERVER,
            virtual_host=MactsExchange.VIRTUAL_HOST,
            credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        publishChannel = conn.channel()

        # command_discovery exchange
        print ".",
        publishChannel.exchange_declare(
            exchange=MactsExchange.COMMAND_DISCOVERY,
            type=MactsExchangeType.FANOUT,
            passive=False,
            durable=False,
            auto_delete=False
        )

        # command_response exchange
        print ".",
        publishChannel.exchange_declare(
            exchange=MactsExchange.COMMAND_RESPONSE,
            type=MactsExchangeType.DIRECT,
            passive=False,
            durable=False,
            auto_delete=False
        )

        # Metrics exchange
        print ".",
        publishChannel.exchange_declare(exchange=MactsExchange.METRICS,
            type=MactsExchangeType.FANOUT,
            passive=False,
            durable=False,
            auto_delete=False
        )

        # Sensor Data exchanges
        print ".",
        publishChannel.exchange_declare(
            exchange=MactsExchange.SENSOR_PREFIX +
                     SensorState.ST_SAVIORS_JUNCTION,
            type=MactsExchangeType.FANOUT,
            passive=False,
            durable=False,
            auto_delete=False
        )

        print ".",
        publishChannel.exchange_declare(
            exchange=MactsExchange.SENSOR_PREFIX +
                     SensorState.RKL_JUNCTION,
            type=MactsExchangeType.FANOUT,
            passive=False,
            durable=False,
            auto_delete=False
        )

        print "DONE!"

class MactsExchangeType:
    FANOUT = "fanout"
    DIRECT = "direct"


class Metric:
    observed = {}

    @classmethod
    def displayList(cls, metricsList):
        for metric in metricsList:
            metric.display()

    def display(self):
        print "METRIC: %s %d %s" % (
            self.observed.get('SimulationId'),
            self.observed.get('SimulationStep'),
            self.observed.get('Observed'))
        print self.observed

    def __init__(self, observationData):
        self.observed = observationData


class SensorState:
    ST_SAVIORS_JUNCTION = "SteSaviors"
    SS_JUNCTION_SENSORS = {
        "e1det_Best~EB_0", "e1det_Best~EB_1",
        "e1det_SteS~SB_0",
        "e1det_BAve~WB_0", "e1det_BAve~WB_1"
    }

    RKL_JUNCTION = "RoseKilnLane"
    RKL_JUNCTION_SENSORS = {
        "e1det_BAve~EB_0", "e1det_BAve~EB_1",
        "e1det_RKL~SB_0", "e1det_RKL~SB_1",
        "e1det_Pell~WB_0", 'e1det_Pell~WB_1'
    }

    SIMULATION_ID = "SimulationId"
    SIMULATION_STEP = "SimulationStep"
    JUNCTION = "Junction"

    sensed = {}

    def display(self):
        print "SENSORS: %s %d %s" % (
            self.sensed.get(self.SIMULATION_ID),
            self.sensed.get(self.SIMULATION_STEP),
            self.sensed.get(self.JUNCTION))
        print self.sensed

    def __init__(self, simulationId, simulationStep, associatedJunction):
        self.sensed.update({
            self.SIMULATION_ID: simulationId,
            self.SIMULATION_STEP: simulationStep,
            self.JUNCTION: associatedJunction
        })

        self.junction = associatedJunction
