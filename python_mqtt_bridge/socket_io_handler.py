"""
python socket io based module to be an API bridge for ProtoPieConnect
"""

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"


# All the main imports
# import sys
# import os
import socketio

# -- [SOCKET IO SCHEME] -- #
io = socketio.Client()
# io = socketio.AsyncClient()

# --- SOCKETIO -> MQTT  --- #
# import preload
from preload import BRIDGE_NAME
from preload import subs_msgids_list
from preload import subs_values_list
from preload import pub_topics_list
from preload import pub_payloads_list
from mqtt_handler import mqtt_client


@io.on('connect')
def on_connect():
    """ On connect & before emitting ‘ppMessage’ event, ‘ppBridgeApp’ event should be emitted"""
    print('[SOCKET_IO] CONNECTED to ProtoPieConnect server!')
    # as per the documentation:
    # https://protopie.notion.site/ProtoPie-Connect-After-Free-Plan-e839babd3c6f4db8ba4f1ab4f9e22f05
    io.emit('ppBridgeApp', {'name': BRIDGE_NAME})
    io.emit('ppMessage', {'messageId': 'status', 'value': 'connected'})

@io.on('disconnect')
def on_disconnect():
    """ On dis-connect, notify """
    print("[SOCKET_IO] DIS-CONNECTED from ProtoPieConnect!")

@io.on('ppMessage')
def on_message(data):
    """ Callback func that fires when a socketio message is received """
    protopie_message_id = data['messageId']
    protopie_value = data['value'] if 'value' in data else None
    # [NOTE]: Both the messageId and the value received from ProtoPieConnect are apparently, ALWAYS of type <str>
    print('[SOCKET_IO] Received a Message from ProtoPieConnect server:', protopie_message_id, ':', protopie_value)
    # Relay from PrototPieConnect's socketio server -> MQTT broker a/c to business logic
    # MAPPINGS (BUSINESS LOGIC):
    mqtt_topic = None
    mqtt_msg = None
    # For all the socketio messageIds listed in the config file
    for i in range(len(subs_msgids_list)):
        #  if one of the messageIds matches with our input sockeio messageIds
        if subs_msgids_list[i] == protopie_message_id:
            # then, pick and set the respective mqtt topic value as the one for mqtt publish method
            mqtt_topic = pub_topics_list[i]
            # if the associated value in the config file,
            # is not a <str> 'value'
            if subs_values_list[i] != 'value' and pub_payloads_list[i] != 'payload':
                # And if, the recieved socketio value is in the config file (expected payload)
                if subs_values_list[i] == protopie_value:
                    # then, set the mqtt pub msg as the correcponding value for that socketio value,
                    # from the config file
                    mqtt_msg = pub_payloads_list[i]
                    pass
            # also, if the associated socketio valkue in the config file,
            # for that received messageid is <str> 'value',
            # it simply means, replay the received socketio value, as it is, as the mqtt payload.
            if subs_values_list[i] == 'value' and pub_payloads_list[i] == 'payload':
                mqtt_msg = protopie_value
        if subs_msgids_list[i] != protopie_message_id:
            print('[SOCKET_IO] The pattern is not in our config file.')
            print('[SOCKET_IO] So don\'t know what to do with it')
            mqtt_topic = None
            mqtt_msg = None
    if mqtt_client.is_connected() and mqtt_topic is not None and mqtt_client is not None:
        print(
            '[MQTT] Relaying topic:\'' + mqtt_topic +
            '\', message:\'' + mqtt_msg + '\' to MQTT broker')
        mqtt_client.publish(mqtt_topic, mqtt_msg)



def start_client(addr, port):
    """ When called, will try to connect to the socket io server (in this case, ProtoPieConnect's server)"""
    protopie_connect_addr = 'http://' + addr + ':' + str(port)
    print("")
    print('[SOCKET_IO] Connecting to ProtoPieConnect server @ ', protopie_connect_addr, ' ...')
    io.connect(protopie_connect_addr)

def stop_client():
    """ When called, will try to connect to the socket io server (in this case, ProtoPieConnect's server)"""
    if io is not None and io.connected:
        print('[SOCKET_IO] Dis-Connecting from ProtoPieConnect')
        io.disconnect()
