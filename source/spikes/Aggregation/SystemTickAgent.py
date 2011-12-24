__author__ = 'k0emt'
import time
import pika
import Infrastructure

#import json
# implements/extends Producer
# code this then extract Producer from it


class SystemTickAgent:
    def __init__(self):
        print "System Tick Agent"
        print "Connecting to RabbitMQ...",
        credentials = pika.PlainCredentials(Infrastructure.APP_USER,
            Infrastructure.APP_PASS)
        conn_params = pika.ConnectionParameters(
            host=Infrastructure.RABBITMQ_SERVER,
            virtual_host=Infrastructure.VHOST_AGGREGATE,
            credentials=credentials)
        conn = pika.BlockingConnection(conn_params)
        self.channel = conn.channel()
        print "CONNECTED"

    def sendTick(self, message):
    #        msg = '{"tick":' + repr(message) + "}"
    #        print msg
    #        print json.loads(msg)
        print message,
        msg = repr(message)
        msg_props = pika.BasicProperties()
        msg_props.content_type = "text/plain"

        self.channel.basic_publish(body=msg,
            exchange=Infrastructure.EXCHANGE_SYSTEM_TICK,
            properties=msg_props,
            routing_key="")
        print "...SENT"

    def autoTick(self, tickDelayInSeconds, timesToTick):
        counter = 0
        while counter < timesToTick:
            time.sleep(tickDelayInSeconds)
            counter += 1
            self.sendTick(counter)


def main():
    sta = SystemTickAgent()
    sta.autoTick(.5, 5)
    sta.sendTick(Infrastructure.STOP_PROCESSING_MESSAGE)

main()
