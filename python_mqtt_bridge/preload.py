#!/usr/bin/env python3
"""
Load the API configs from the dot env files
"""

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"

# All the main imports
import fileinput
import sys
import os
import time
from dotenv import load_dotenv
import json

# Load the variables from env file
load_dotenv()

# Assign the appropriate variables respectively 
PROTO_PIE_CONNECT_HOST = os.environ.get('PROTO_PIE_CONNECT_HOST', 'localhost')
PROTO_PIE_CONNECT_PORT = os.environ.get('PROTO_PIE_CONNECT_PORT', 9981)
# protopie_connect_addr = 'http://' + PROTO_PIE_CONNECT_HOST + ':' + str(PROTO_PIE_CONNECT_PORT)

BRIDGE_NAME = os.environ.get('APP_NAME', 'python_mqtt_bridge')
MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', '127.0.0.1')
MQTT_BROKER_PORT = os.environ.get('MQTT_BROKER_PORT', 1883)
# subs_topic_list = ["ROOM", "BRIGHTNESS"]
subs_topic_list = json.loads(os.environ.get('MSG_IDS'))
