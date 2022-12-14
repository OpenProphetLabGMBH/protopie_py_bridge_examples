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
    # If message ID received doesn't exist in our config file, stop and exit the func
    if _protopie_msg_id not in subs_msgids_list:
        if not tui_mode:
            print('\n[SOCKET_IO] Received msgID doesn\'t exists in our config')
            print('[SOCKET_IO] Hence not publishing anything ...\n')
        else:
            pl.output_msg_buff = ['', '[SOCKET_IO] msgID or it\'s value doesn\'t exists in config',
                                  '[SOCKET_IO] Hence can\'t proceed with SIO->MQTT mapping!', '']
        return

    # Get the idx for the received messageID as now this is confirmed
    # to be in our list of messageIDs we want to listen to
    msg_id_idx = subs_msgids_list.index(_protopie_msg_id)
    # Set the respective mqtt publishing topic, corresponding to that messageID
    _mqtt_topic = pub_topics_list[msg_id_idx]

    # If message's value received doesn't exist in our config file and at that idx and
    # it is not equql to <str> 'value', stop and exit the func
    if _protopie_value not in subs_values_list and subs_values_list[msg_id_idx] != 'raw_value':
        if not tui_mode:
            print('\n[SOCKET_IO] Received msg value doesn\'t exists in our config.')
            print('[SOCKET_IO] Neither it has been set to be transmitted as it is.')
            print('[SOCKET_IO] Hence can\'t proceed with SIO->MQTT mapping!\n')
        else:
            pl.output_msg_buff = ['', '[SOCKET_IO] value doesn\'t exists in config',
                                  '[SOCKET_IO] Neither it has been set to be transmitted as it is.',
                                  '[SOCKET_IO] Hence can\'t proceed with SIO->MQTT mapping!', '']
        return
    elif _protopie_value in subs_values_list and subs_values_list[msg_id_idx] != 'raw_value':
        # update the msg idx.
        msg_id_idx = subs_values_list.index(_protopie_value)

    if pub_payloads_list[msg_id_idx] == 'raw_payload':
        _mqtt_payload = _protopie_value
    else:
        _mqtt_payload = pub_payloads_list[msg_id_idx]

    # if mqtt topic didn't get assigned, can't publish
    if _mqtt_topic is None:
        if not tui_mode:
            print('[MQTT] Topic wasn\'t successfully assigned (None)!')
            print('[MQTT] Hence not proceeding with publishing MQTT msg!')
        else:
            pl.output_msg_buff = ['[MQTT] Topic not successfully assigned (None)!',
                                  '[MQTT] Hence not proceeding with publishing MQTT msg!']
        return

    # if mqtt payload didn't get assigned, can't publish
    if _mqtt_payload is None:
        if not tui_mode:
            print('[MQTT] Payload wasn\'t successfully assigned (None)!')
            print('[MQTT] Hence not proceeding with publishing MQTT msg!')
        else:
            pl.output_msg_buff = ['[MQTT] Payload not successfully assigned (None)!',
                                  '[MQTT] Hence not proceeding with publishing MQTT msg!']
        return

    # if our mqtt client doesn't exist
    if mqtt_client is None:
        #  client doesn't exist
        if not tui_mode:
            print('\n[MQTT] ** MQTT client doesn\'t exist!')
            print('[MQTT] Hence not proceeding with publishing MQTT msg!')
            print('But here the MQTT message:')
            print('topic:\'' + _mqtt_topic +
                  '\', message:\'' + _mqtt_payload + '\' to MQTT broker')
        else:
            pl.output_msg_buff = ['', '[MQTT] ** MQTT client doesn\'t exist',
                                  '[MQTT] Hence not proceeding with publishing MQTT msg!', '']
        return
    # if mqtt client is not connected to Broker
    if not mqtt_client.is_connected():
        if not tui_mode:
            print('\n[MQTT] ** Not connected to MQTT broker!')
            print('[MQTT] Hence not proceeding with publishing MQTT msg!')
            print('But here the MQTT message:')
            print('topic:\'' + _mqtt_topic +
                  '\', message:\'' + _mqtt_payload + '\' to MQTT broker')
        else:
            pl.output_msg_buff = ['', '[MQTT] ** Not connected to MQTT broker!',
                                  '[MQTT] Hence not proceeding with publishing MQTT msg!!', '']
        return

    print('[MQTT][PUB] topic:\'' + _mqtt_topic +
          '\', message:\'' + _mqtt_payload + '\' to MQTT broker')

    if not tui_mode:
        print('[MQTT] Relaying that MQTT message now!')
    else:
        pl.output_msg_buff = ['[MQTT] Relaying that MQTT message now!']

    mqtt_client.publish(_mqtt_topic, _mqtt_payload)


@io.on('ppMessage')
def on_message(data):
    ''' Callback func that fires when a socketio message is received '''
    # [NOTE]: Both the messageId and the value received from ProtoPieConnect are apparently, ALWAYS of type <str>
    protopie_msg_id = data['messageId']
    protopie_msg_id = protopie_msg_id.strip()

    protopie_value = data['value'] if 'value' in data else None
    protopie_value = protopie_value.strip()

    if protopie_value is None:
        if not tui_mode:
            print('[SOCKET_IO] pp Value received is None! Can\'t proceed!')
        else:
            pl.output_msg_buff = ['[SOCKET_IO] pp Value received is None! Can\'t proceed!']
        return

    if not tui_mode:
        print('[SOCKET_IO] Received a Message from ProtoPieConnect server: ' + protopie_msg_id + ':' + protopie_value)
    else:
        # [BUG] [Not getting printed don't know why]
        pl.output_msg_buff = ['SOCKET_IO] Received a Message from ProtoPieConnect server:' +
                              protopie_msg_id + ':' + protopie_value]

    # MAPPINGS (BUSINESS LOGIC):
    if protopie_value == 'raw_value' or protopie_value == 'raw_payload':
        # Can't use this as a value in Protopie Studio to send signal
        # as it is a revserved for config file's relay conventions
        if not tui_mode:
            print('[SOCKET_IO] received message: \'' + protopie_value + '\' can\'t be used as it is reserved')
        else:
            # [BUG] [Not getting printed don't know why]
            pl.output_msg_buff = ['SOCKET_IO] \'' + protopie_value + '\' can\'t be used as it is reserved']
        return

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
