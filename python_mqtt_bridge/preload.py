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
import yaml
import json

def clear():
    """ Func for clearing screen based on OS """
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

# Clear the screen
clear()
print("")

verbose = True

try:
    file_stream = open('config.yaml', 'r')
except IOError:
    file_stream = None
    print("Note: config file doesn't exists")
    print('Make sure you have \'config.yaml\' in the same directory as teh scripts!')
    exit(0)

configs = yaml.safe_load(file_stream)
# print(configs['protopie_host'])

# Assign the comm network connect creds
PROTO_PIE_CONNECT_HOST = configs['protopie_host']
PROTO_PIE_CONNECT_PORT = configs['protopie_port']

BRIDGE_NAME = configs['bridge_name']
MQTT_BROKER_HOST = configs['mqtt_broker_host']
MQTT_BROKER_PORT = configs['mqtt_broker_port']

SOCKETIO_TO_MQTT_MAPPING = configs['mapping']['socketio_to_mqtt']
MSGIDS_TO_TOPICS_LIST = SOCKETIO_TO_MQTT_MAPPING['msgid_to_topic']
VALUES_TO_PAYLOADS_LIST = SOCKETIO_TO_MQTT_MAPPING['value_to_payload']

MQTT_TO_SOCKETIO_MAPPING = configs['mapping']['mqtt_to_socketio']
TOPICS_TO_MSGIDS_LIST = MQTT_TO_SOCKETIO_MAPPING['topic_to_msgid']
PAYLOADS_TO_VALUES_LIST = MQTT_TO_SOCKETIO_MAPPING['payload_to_value']

# --- MQTT -> SOCKETIO --- #
subs_topics_list = []
emmission_msgids_list = []
for topic_to_msgid in TOPICS_TO_MSGIDS_LIST:
    # Extact subscription topics
    subs_topics_list.append(topic_to_msgid[0])
    # Extract socketio messageIDs
    emmission_msgids_list.append(topic_to_msgid[1])

subs_payloads_list = []
emmission_values_list = []
for payload_to_value in PAYLOADS_TO_VALUES_LIST:
    # Extact payloads, respective to subscription topics
    subs_payloads_list.append(payload_to_value[0])
    # Extact values, that will replace the respective payloads
    emmission_values_list.append(payload_to_value[1])

# Check lengths to ensure data pattern
if (len(subs_topics_list) == len(subs_payloads_list) and len(emmission_msgids_list) == len(emmission_values_list)):
    if verbose:
        print("Mapping for MQTT -> socketio:")
        print("-----------------------------")
        for i in range(len(subs_topics_list)):
            print('For MQTT TOPIC:\'' + subs_topics_list[i] + '\' and PAYLOAD:\'' + subs_payloads_list[i] +
                  '\', the respective socketio translation is, MESSAGE_ID:\'' + emmission_msgids_list[i] +
                  '\' VALUE:\'' + emmission_values_list[i] + '\'')
        print("")
    pass
else:
    print("Mapping patterns don't match!")
    print("Check the config file!")

# --- SOCKETIO -> MQTT --- #
# TBD
