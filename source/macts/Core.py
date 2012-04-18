__author__ = 'k0emt'

import pika
import json

MQ_SERVER = "localhost"  # YOUR RABBITMQ SERVER NAME/IP HERE
VIRTUAL_HOST = "macts"
STOP_PROCESSING_MESSAGE = "QRT"


class Agent:
    """
    Base class for all Agents in the system
    """
    NAME = None
    PASSWORD = None

    COMM_AGENT_NAME = "liaison"
    COMM_AGENT_PASSWORD = "talker"

    METRICS_AGENT_NAME = "metrics"
    METRICS_AGENT_PASSWORD = "countem"

    simulationId = "NotSet"
    simulationStep = 1
    verbose_level = 0

    def Connect_RabbitMQ(self):
        print "Connecting to RabbitMQ...",
        credentials = pika.PlainCredentials(self.NAME, self.PASSWORD)
        conn_params = pika.ConnectionParameters(
            host=MQ_SERVER,
            virtual_host=VIRTUAL_HOST,
            credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        channel = conn.channel()
        self.publishChannel = conn.channel()
        print "CONNECTED"
        return channel

    def establish_connection(self, message_consumer, subscribed_exchange):
        channel = self.Connect_RabbitMQ()

        print "Creating Queue for %s exchange..." % subscribed_exchange,
        ourChan = channel.queue_declare(exclusive=True)
        channel.queue_bind(exchange=subscribed_exchange,
            queue=ourChan.method.queue)
        print "DONE"
        print "Setting up callback...",

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(message_consumer)
        print "DONE"

        print "Monitoring Queue"
        channel.start_consuming()
        print "%s %s FINISHED" % (self.NAME, subscribed_exchange)

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

    def isStopProcessingMessage(self, body):
        return STOP_PROCESSING_MESSAGE == json.loads(body)


class MactsExchange:
    METRICS = "metrics"
    SENSOR_PREFIX = "sensor-"


class MactsExchangeType:
    FANOUT = "fanout"


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
