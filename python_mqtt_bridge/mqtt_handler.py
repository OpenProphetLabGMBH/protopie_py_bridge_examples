'''
python paho based module to redirect MQTT messages to Protopie socket messages and vice-versa
'''

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"

# import os
# import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import paho.mqtt.client as mqtt

# --- MQTT -> SOCKETIO --- #
from socket_io_handler import io

# import preload
import preload as pl
from preload import BRIDGE_NAME
from preload import subs_topics_list
from preload import subs_payloads_list
from preload import emmission_msgids_list
from preload import emmission_values_list
from preload import tui_mode
import time


mqtt_client = mqtt.Client(
    client_id=BRIDGE_NAME,
    clean_session=False,
    userdata=None,
    # protocol=MQTTv311,
    transport="tcp")


def on_broker_connect(client, userdata, flags, rc):
    ''' Callback func that fires on connecting to a broker '''
    if not tui_mode:
        print('\n[MQTT] CONNECTED to BROKER !')
    else:
        pl.output_msg_buff = ['', '[MQTT] CONNECTED to BROKER !']
    # subscribe to topic list upon connection
    # Note: if multiple same topics subscribe only once ...
    topics_list_set = set(subs_topics_list)
    unique_topics_list = (list(topics_list_set))
    for topic in unique_topics_list:
        mqtt_client.subscribe(topic)
        if not tui_mode:
            print('[MQTT] SUBSCRIBED to TOPIC: \'' + topic + '\'')
        else:
            pl.output_msg_buff = ['[MQTT] SUBSCRIBED to TOPIC: \'' + topic + '\'']
            time.sleep(0.01)  # short delay or the buffer doesn't get printed in serialization

def on_broker_disconnect(client, userdata, rc):
    ''' Callback func that fires on getting disconnected from a broker '''
    if not tui_mode:
        print('[MQTT] DIS-CONNECTED from BROKER!')

def map_io(_mqtt_topic, _mqtt_payload, _protopie_msg_id, _protopie_value):
    ''' A function that directs the inputs, based on the config file, to the output pattern '''
    # For all the MQTT topics listed in the config file
    for i in range(len(subs_topics_list)):
        #  if one of the topics matches with our input MQTT topic
        if subs_topics_list[i] == _mqtt_topic:
            # then, pick and set the respective socketio msg value as the one for socketio emit method
            _protopie_msg_id = emmission_msgids_list[i]
            # if the associated payload in the config file,
            # is not a <str> 'payload'
            if subs_payloads_list[i] != 'raw_payload' and emmission_values_list[i] != 'raw_value':
                # And if, the recieved payload is in the config file (expected payload)
                if subs_payloads_list[i] == _mqtt_payload:
                    # then, set the socketio emit value as the correcponding value for that payload,
                    # from the config file
                    _protopie_value = emmission_values_list[i]
            # Also, if the associated payload in the config file,
            # for that received topic is <str> 'payload',
            # it simply means, replay the received mqtt payload, as it is, as the socketio value.
            if subs_payloads_list[i] == 'raw_payload' and emmission_values_list[i] == 'raw_value':
                _protopie_value = _mqtt_payload
    if _protopie_msg_id is not None and _protopie_value is not None:
        if io.connected:
            if not tui_mode:
                print(
                    '[SOCKET_IO] Relaying MessageId:\'' + _protopie_msg_id +
                    '\', Value:\'' + _protopie_value + '\' to ProtoPieConnect server')
            else:
                pl.output_msg_buff = ['[SOCKET_IO] Relaying MessageId:\'' + _protopie_msg_id +
                                      '\', Value:\'' + _protopie_value + '\'']
            io.emit('ppMessage', {'messageId': _protopie_msg_id, 'value': _protopie_value})
        else:
            if not tui_mode:
                print('\n** Not connected to socketio server ...')
                print('Hence not emitting ...')
                print('But messageId:', _protopie_msg_id, 'value:', _protopie_value, '\n')
            else:
                pl.output_msg_buff = ['', '** Not connected to socketio server ...',
                                      'Hence not emitting ...', 'But messageId:' +
                                      _protopie_msg_id + ' value:' + _protopie_value, '']
    else:
        if not tui_mode:
            print('\n** ALERT: One of the required value for socketio transmission is None')
            print('MessageId: ', _protopie_msg_id, ', Value: ', _protopie_value)
            print('Hence, Not emitting ...\n')
        else:
            pl.output_msg_buff = ['', '** ALERT: One of the required value for socketio transmission is None',
                                  'MessageId: ' + str(_protopie_msg_id) + ', Value: ' + str(_protopie_value),
                                  'Hence, not emitting ...', '']

def on_message_from_broker(client, userdata, msg):
    ''' Callback func that fires when we receive a message from the broker '''
    # Relay from MQTT -> socketio for PrototPieConnect method
    # [NOTE]:
    # 1. All the 'topics' and 'payloads' are of type <byte> as that's how the MQTTmessage class works.
    # 2. All the values need to be converted to <str> or else io.emit doesn't send the value'
    if type(msg.topic) is not str:
        mqtt_topic = str(msg.topic, 'utf-8')
    else:
        mqtt_topic = msg.topic
    if type(msg.payload) is not str:
        mqtt_payload = str(msg.payload, 'utf-8')
    else:
        mqtt_payload = msg.payload
    if not tui_mode:
        print('\n[MQTT] RECEIVED Topic:\'' + mqtt_topic + '\', Message:\'' +
              mqtt_payload + '\' + from MQTT broker')
    else:
        # [BUG] [Not getting printed don't know why]
        pl.output_msg_buff = ['', '[MQTT] RECEIVED Topic:\'' + mqtt_topic + '\', Message:\'' + mqtt_payload + '\'', '']
    # MAPPINGS (BUSINESS LOGIC):
    protopie_msg = None
    protopie_value = None
    map_io(mqtt_topic, mqtt_payload, protopie_msg, protopie_value)

# Secure mqtt based on if security is enabled or not
from preload import MQTT_SECURED
if MQTT_SECURED:
    from preload import MQTT_USR_NAME
    from preload import MQTT_PWD
    mqtt_client.username_pw_set(MQTT_USR_NAME, MQTT_PWD)

mqtt_client.on_connect = on_broker_connect
mqtt_client.on_disconnect = on_broker_disconnect
mqtt_client.on_message = on_message_from_broker


def start_client(addr, port):
    ''' Will try to connect to broker and start a non-blocking loop '''
    if not tui_mode:
        print('\n[MQTT] Connecting to BROKER @ mqtt://' + addr + ':' + str(port) + ' ...')
    mqtt_client.connect_async(addr, port=int(port), keepalive=60)
    mqtt_client.loop_start()  # Non blocking loop method

def stop_client():
    ''' Will try to stop the thread and dis-connect from broker '''
    if mqtt_client is not None and mqtt_client.is_connected():
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
