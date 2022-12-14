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
    topic_idx = subs_topics_list.index(_mqtt_topic)
    _protopie_msg_id = emmission_msgids_list[topic_idx]

    if _mqtt_payload not in subs_payloads_list and subs_payloads_list[topic_idx] != 'raw_payload':
        # received payload doesn't exist in config file 
        # and it is not 'raw_payload'
        if not tui_mode:
            print('[MQTT] Received payload doesn\'t exist in config file!')
            print('[MQTT] Neither it has been set to be transmitted as it is.')
            print('[MQTT] Hence can\'t proceed with MQTT->SIO mapping!\n')
        else:
            pl.output_msg_buff = ['', '[MQTT] Received payload doesn\'t exists in config',
                                  '[MQTT] Neither it has been set to be transmitted as it is.',
                                  '[MQTT] Hence can\'t proceed with MQTT->SIO mapping!', '']
        return
    elif _mqtt_payload in subs_payloads_list and subs_payloads_list[topic_idx] != 'raw_payload':
        # update the msg idx.
        topic_idx = subs_payloads_list.index(_mqtt_payload)

    if emmission_values_list[topic_idx] == 'raw_value':
        _protopie_value = _mqtt_payload
    else:
        _protopie_value = emmission_values_list[topic_idx]

    # if sio msd id didn't get assigned, can't publish
    if _protopie_msg_id is None:
        if not tui_mode:
            print('[SOCKET_IO] MessaegId wasn\'t successfully assigned (None)!')
            print('[SOCKET_IO] Hence not proceeding with publishing sio msg!')
        else:
            pl.output_msg_buff = ['[SOCKET_IO] MessaegId not successfully assigned (None)!',
                                  '[SOCKET_IO] Hence not proceeding with publishing sio msg!']
        return

    # if sio msg value didn't get assigned, can't publish
    if _protopie_value is None:
        if not tui_mode:
            print('[SOCKET_IO] Value wasn\'t successfully assigned!')
            print('[SOCKET_IO] Hence not proceeding with publishing sio msg!')
        else:
            pl.output_msg_buff = ['[SOCKET_IO] Value not successfully assigned (None)!',
                                  '[SOCKET_IO] Hence not proceeding with publishing sio msg!']
        return

    # if sio client doesn't exist
    if not io:
        if not tui_mode:
            print('\n[SOCKET_IO] ** sio client doesn\'t exist!')
            print('[SOCKET_IO] Hence not proceeding with publishing sio msg!')
            print('But here the sio message:')
            print('MessageId:\'' + _protopie_msg_id +
                  '\', Value:\'' + _protopie_value + '\' to ProtoPieConnect server')
        else:
            pl.output_msg_buff = ['', '[SOCKET_IO] ** sio client doesn\'t exist!',
                                  '[SOCKET_IO] Hence not proceeding with publishing sio msg!', '']
        return

    # if our sio client is not connected to ProtoPieConnect server
    if not io.connected:
        if not tui_mode:
            print('\n[SOCKET_IO] ** sio client not connected to ppConnect server!')
            print('[SOCKET_IO] Hence not proceeding with publishing sio msg!')
            print('But here the sio message:')
            print('MessageId:\'' + _protopie_msg_id +
                  '\', Value:\'' + _protopie_value + '\' to ProtoPieConnect server')
        else:
            pl.output_msg_buff = ['', '[SOCKET_IO] ** sio client not connected to ppConnect server!',
                                  '[SOCKET_IO] Hence not proceeding with publishing sio msg!', '']
        return

    if not tui_mode:
        print(
            '[SOCKET_IO] Relaying MessageId:\'' + _protopie_msg_id +
            '\', Value:\'' + _protopie_value + '\' to ProtoPieConnect server')
    else:
        pl.output_msg_buff = ['[SOCKET_IO] Relaying MessageId:\'' + _protopie_msg_id +
                              '\', Value:\'' + _protopie_value + '\'']

    io.emit('ppMessage', {'messageId': _protopie_msg_id, 'value': _protopie_value})


def on_message_from_broker(client, userdata, msg):
    ''' Callback func that fires when we receive a message from the broker '''
    # Relay from MQTT -> socketio for PrototPieConnect method
    # [NOTE]:
    # 1. All the 'topics' and 'payloads' are of type <byte> as that's how the MQTTmessage class works.
    # 2. All the values need to be converted to <str> or else io.emit doesn't send the value'
    if type(msg.topic) is not str:
        mqtt_topic = str(msg.topic, 'utf-8')
        mqtt_topic = mqtt_topic.strip()
    else:
        mqtt_topic = msg.topic
    if type(msg.payload) is not str:
        mqtt_payload = str(msg.payload, 'utf-8')
    else:
        mqtt_payload = msg.payload
        mqtt_payload = mqtt_payload.strip()
     
    if not tui_mode:
        print('\n[MQTT] RECEIVED Topic:\'' + mqtt_topic + '\', Message:\'' +
              mqtt_payload + '\' + from MQTT broker')
    else:
        # [BUG] [Not getting printed don't know why]
        pl.output_msg_buff = ['', '[MQTT] RECEIVED Topic:\'' + mqtt_topic + '\', Message:\'' + mqtt_payload + '\'', '']
   
    # MAPPINGS (BUSINESS LOGIC):
    if mqtt_payload == 'raw_payload' or mqtt_payload == 'raw_value':
        # Can't use this as a value in Protopie Studio to send signal
        # as it is a revserved for config file's relay conventions
        if not tui_mode:
            print('[MQTT] received payload: \'' + mqtt_payload + '\' can\'t be used as it is reserved')
        else:
            # [BUG] [Not getting printed don't know why]
            pl.output_msg_buff = ['[MQTT] \'' + mqtt_payload + '\' can\'t be used as it is reserved']
        return

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
