'''
python socket io based module to be an API bridge for ProtoPieConnect
'''

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"

# import os
# import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# All the main imports
import socketio
from time import sleep

# -- [SOCKET IO SCHEME] -- #
io = socketio.Client()
# io = socketio.AsyncClient()

# --- SOCKETIO -> MQTT  --- #
from preload import BRIDGE_NAME
from preload import subs_msgids_list
from preload import subs_values_list
from preload import pub_topics_list
from preload import pub_payloads_list
from preload import tui_mode
import preload as pl

if __name__ != '__main__':
    from mqtt_handler import mqtt_client



@io.on('connect')
def on_connect():
    ''' On connect & before emitting ‘ppMessage’ event, ‘ppBridgeApp’ event should be emitted '''
    if not tui_mode:
        print('\n[SOCKET_IO] CONNECTED to ProtoPieConnect server!')
    else:
        pl.output_msg_buff = ['', '[SOCKET_IO] CONNECTED to ProtoPieConnect server!']
    # as per the documentation:
    # https://protopie.notion.site/ProtoPie-Connect-After-Free-Plan-e839babd3c6f4db8ba4f1ab4f9e22f05
    io.emit('ppBridgeApp', {'name': BRIDGE_NAME})
    io.emit('ppMessage', {'messageId': 'status', 'value': 'connected'})

@io.on('disconnect')
def on_disconnect():
    ''' On dis-connect, notify '''
    if not tui_mode:
        print("[SOCKET_IO] DIS-CONNECTED from ProtoPieConnect!")


def map_io(_protopie_msg_id, _protopie_value, _mqtt_topic, _mqtt_payload):
    ''' A function that directs the inputs, based on the config file, to the output pattern '''
    # Do a check if the received message is in our config list
    if _protopie_msg_id in subs_msgids_list and _protopie_value in subs_values_list:
        # Relay from PrototPieConnect's socketio server -> MQTT broker a/c to business logic
        # MAPPINGS (BUSINESS LOGIC):
        # For all the socketio messageIds listed in the config file
        for i in range(len(subs_msgids_list)):
            #  if one of the messageIds matches with our input sockeio messageIds
            if subs_msgids_list[i] == _protopie_msg_id:
                # then, pick and set the respective mqtt topic value as the one for mqtt publish method
                _mqtt_topic = pub_topics_list[i]
                # if the associated value in the config file is not a <str> 'value' of below type
                if subs_values_list[i] != 'raw_value' and pub_payloads_list[i] != 'raw_payload':
                    # And if, the recieved socketio value is in the config file (expected payload)
                    if subs_values_list[i] == _protopie_value:
                        # then, set the mqtt pub msg as the correcponding value for that socketio value,
                        # from the config file
                        _mqtt_payload = pub_payloads_list[i]
                        pass
                # also, if the associated socketio value in the config file,
                # for that received messageid is of <str> 'value' of below type,
                # it simply means, replay the received socketio value, as it is, as the mqtt payload.
                if subs_values_list[i] == 'raw_value' and pub_payloads_list[i] == 'raw_payload':
                    _mqtt_payload = _protopie_value

        if _mqtt_topic is not None and mqtt_client is not None:
            if mqtt_client.is_connected():
                if not tui_mode:
                    print(
                        '[MQTT] Relaying topic:\'' + _mqtt_topic +
                        '\', message:\'' + _mqtt_payload + '\' to MQTT broker')
                else:
                    pl.output_msg_buff = ['[MQTT] Relaying topic:\'' + _mqtt_topic +
                                          '\', message:\'' + _mqtt_payload + '\' to MQTT broker']
                mqtt_client.publish(_mqtt_topic, _mqtt_payload)
            else:
                if not tui_mode:
                    print('\n** Not connected to MQTT broker ...')
                    print('Hence not publishing ...')
                    print('But topic:' + _mqtt_topic + ' payload:' + _mqtt_payload, '\n')
                else:
                    pl.output_msg_buff = ['', '** Not connected to MQTT broker, so not publishing',
                                          'But topic:' + _mqtt_topic + ' payload:' + _mqtt_payload, '']
        else:
            if not tui_mode:
                print('\n** ALERT: One of the required value for mqtt publishing is None')
                print('Topic: ' + _mqtt_topic + ', payload: ' + _mqtt_payload)
                print('Not publishing ...\n')
            else:
                pl.output_msg_buff = ['', '** ALERT: One of the required value for mqtt publishing is None',
                                      'Topic: ' + str(_mqtt_topic) + ', payload: ' + str(_mqtt_payload),
                                      'Not publishing ...']
                # return
    else:
        if not tui_mode:
            print('\n[SOCKET_IO] Either the received msgID or it\'s value doesn\'t exists in our config')
            print('[SOCKET_IO] Hence not publishing anything ...\n')
        else:
            pl.output_msg_buff = ['', '[SOCKET_IO] msgID or it\'s value doesn\'t exists in config',
                                  'Hence not publishing anything ...', '']


@io.on('ppMessage')
def on_message(data):
    ''' Callback func that fires when a socketio message is received '''
    protopie_msg_id = data['messageId']
    protopie_value = data['value'] if 'value' in data else None
    # [NOTE]: Both the messageId and the value received from ProtoPieConnect are apparently, ALWAYS of type <str>
    if not tui_mode:
        print('[SOCKET_IO] Received a Message from ProtoPieConnect server:' + protopie_msg_id + ':' + protopie_value)
    else:
        # [BUG] [Not getting printed don't know why]
        pl.output_msg_buff = ['SOCKET_IO] Received a Message from ProtoPieConnect server:' +
                              protopie_msg_id + ':' + protopie_value]
    mqtt_topic = None
    mqtt_payload = None
    map_io(protopie_msg_id, protopie_value, mqtt_topic, mqtt_payload)



def start_client(addr, port):
    ''' When called, will try to connect to the socket io server (in this case, ProtoPieConnect's server) '''
    protopie_connect_addr = 'http://' + addr + ':' + str(port)
    '''
    Note: Only at first launch, if it can't find the protopie connect server,
          it will go in a loop for it to be available
    '''
    while True:
        try:
            if not tui_mode:
                print('\n[SOCKET_IO] Trying to connect to ProtoPieConnect server @ ', protopie_connect_addr, ' ...')
            io.connect(protopie_connect_addr)
        except Exception:
            if not tui_mode:
                print("[SOCKET_IO] Couldn't find sio server! Sure it's configured correctly and running?\n")
            pass
        else:
            io.wait()
            #  Needed this wait here or else clean exit doesn't happen
            #  More here:https://github.com/miguelgrinberg/python-socketio/issues/301
            break
        sleep(2)


def stop_client():
    ''' When called, will try to connect to the socket io server (in this case, ProtoPieConnect's server) '''
    if io is not None and io.connected:
        if not tui_mode:
            print('[SOCKET_IO] Dis-Connecting from ProtoPieConnect')
        io.disconnect()
