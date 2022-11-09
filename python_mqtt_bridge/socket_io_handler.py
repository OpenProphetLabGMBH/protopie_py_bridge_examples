"""
python socket io based module to be an API bridge for ProtoPieConnect
"""

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"


# All the main imports
import sys
import os
# import vars
from preload import BRIDGE_NAME
import socketio
# from mqtt_handler import mqtt_client

# -- [SOCKET IO SCHEME] -- #
io = socketio.Client()
# io = socketio.AsyncClient()

@io.on('connect')
def on_connect():
    """ On connect & before emitting ‘ppMessage’ event, ‘ppBridgeApp’ event should be emitted"""
    print('[SOCKET_IO] CONNECTED to ProtoPieConnect server!')
    io.emit('ppBridgeApp', {'name': BRIDGE_NAME})
    io.emit('ppMessage', {'messageId': 'status', 'value': 'connected'})

@io.on('disconnect')
def on_disconnect():
    """ On dis-connect, notify """
    print("[SOCKET_IO] DIS-CONNECTED from ProtoPieConnect!")

@io.on('ppMessage')
def on_message(data):
    message_id = data['messageId']
    value = data['value'] if 'value' in data else None
    # [NOTE]: Both the messageId and the value received from ProtoPieConnect are apparently, ALWAYS of type <str>

    print('[SOCKET_IO] Received a Message from ProtoPieConnect server:', message_id, ':', value)
    print('[SOCKET_IO] type of received value is', type(value))

    # [WIP] Relay from PrototPieConnect's socketio server -> MQTT broker
    # global mqtt_client_connected
    # if mqtt_client_connected:
    #     print('[MQTT] Relaying mqtt data with TOPIC: ', message_id, ' MESSAGE: ', str(value))
    #     mqtt_client.publish(topic=message_id, payload=value, qos=0, retain=False)



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
