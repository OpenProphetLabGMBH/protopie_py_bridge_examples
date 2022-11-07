"""
python paho based module to redirect MQTT messages to Protopie socket messages and vice-versa
"""

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"

import paho.mqtt.client as mqtt
from preload import BRIDGE_NAME
from preload import subs_topic_list
from socket_io_handler import io


mqtt_client = mqtt.Client(
    client_id=BRIDGE_NAME,
    clean_session=False,
    userdata=None,
    # protocol=MQTTv311,
    transport="tcp")

def on_broker_connect(client, userdata, flags, rc):
    """ Callback func that fires on connecting to a broker """
    print('[MQTT] CONNECTED to BROKER with result code: ', rc, '!')
    # mqtt_client_connected = True
    # subscribe to topic list upon connection
    for topic in subs_topic_list:
        mqtt_client.subscribe(topic)
        print('[MQTT] SUBSCRIBED to TOPIC: ' + topic)

def on_broker_disconnect(client, userdata, rc):
    """ Callback func that fires on getting disconnected from a broker """
    print('[MQTT] DIS-CONNECTED from BROKER with result code: ', rc, '!')
    # mqtt_client_connected = False

def on_message_from_broker(client, userdata, msg):
    """ Callback func that fires when we receive a message from the broker """
    # Relay from MQTT -> socketio for PrototPieConnect method
    # [NOTE]s:
    # 1. All the 'topics' and 'payloads' are of type <byte> as that's how the MQTTmessage class works.
    # 2. All the values need to be converted to <str> or else io.emit doesn't send the value'
    protopie_msg = str(msg.topic, 'utf-8')
    protopie_val = str(msg.payload, 'utf-8')
    print('[MQTT] RECEIVED Topic: ' + protopie_msg + ' Message: ' + protopie_val, ' from MQTT broker')
    print('[MQTT] Payload\'s type is:', type(msg.payload))

    print(
        '[SOCKET_IO] Relaying MessageId: ', protopie_msg,
        ' Value: ', protopie_val, ' to ProtoPieConnect server')

    # MAPPINGS:
    # 1. Direct translation MQTT -> SOCKET IO:
    # ----------------------------------------
    # [socket_io] messageId = [MQTT] Topic and [socket_io] value = [MQTT] payload
    if io.connected:
        io.emit('ppMessage', {'messageId': protopie_msg, 'value': protopie_val})

mqtt_client.on_connect = on_broker_connect
mqtt_client.on_disconnect = on_broker_disconnect
mqtt_client.on_message = on_message_from_broker

def start_client(addr, port):
    """ Will try to connect to broker and start a non-blocking loop"""
    print('[MQTT] Connecting to BROKER @ mqtt://' + addr + ':' + str(port) if type(port) is int else port + ' ...')
    mqtt_client.connect_async(addr, port=int(port), keepalive=60)
    mqtt_client.loop_start()  # Non blocking loop method

def stop_client():
    """ Will try to stop the thread and dis-connect from broker"""
    if mqtt_client is not None and mqtt_client.is_connected:
        print('[MQTT] Dis-Connecting from BROKER ...')
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
