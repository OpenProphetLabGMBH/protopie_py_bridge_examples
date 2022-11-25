#!/usr/bin/env python3
'''
python app to redirect MQTT messages to Protopie socket messages and vice-versa
'''

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"

# All the main imports
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from preload import PROTO_PIE_CONNECT_HOST
from preload import PROTO_PIE_CONNECT_PORT
from preload import MQTT_BROKER_HOST
from preload import MQTT_BROKER_PORT

import socket_io_handler as sio_sys
import mqtt_handler as mqtt_sys
import time


def main():
    ''' Main entry point of the app '''
    # [1] First start mqtt service
    mqtt_sys.start_client(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    # [2] Then start the socketio service
    sio_sys.start_client(PROTO_PIE_CONNECT_HOST, PROTO_PIE_CONNECT_PORT)


if __name__ == '__main__':
    ''' This is executed when run from the command line '''
    try:
        main()
    except KeyboardInterrupt:
        mqtt_sys.stop_client()
        sio_sys.stop_client()
        exit(0)
