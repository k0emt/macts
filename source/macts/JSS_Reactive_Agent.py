__author__ = 'k0emt'
import json

from PlanningAgent import BasePlanningAgent
from Core import MactsExchange
from Core import SensorState

class JSS_ReactiveAgent(BasePlanningAgent):
    """
    Reactive Agent for Ste Saviors Junction
    """
    # SR 15 The planning agent examines incoming data and creates a new TLS plan.
    # SR 16 The planning agent submits the plan to the Safety Agent for review.
    # SR 17 is not applicable to this agent

    verbose_level = 1

    def sensor_consumer(self, channel, method, header, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)

        message_received = json.loads(body)
        self.verbose_display("SC: %s", message_received, 1)

    def __init__(self):
        BasePlanningAgent.__init__(self)
        self.agent_name = "JSS_ReactiveAgent"
        print self.agent_name + " Agent ONLINE"

        self.Connect_RabbitMQ()

        self.establish_connection("commands",
            self.command_consumer
            , MactsExchange.COMMAND_DISCOVERY)

        self.establish_connection("sensor",
            self.sensor_consumer,
            MactsExchange.SENSOR_PREFIX + SensorState.ST_SAVIORS_JUNCTION
        )

        self.start_consuming()

        print self.agent_name + " Agent OFFLINE"

if __name__ == "__main__":
    JSS_ReactiveAgent()