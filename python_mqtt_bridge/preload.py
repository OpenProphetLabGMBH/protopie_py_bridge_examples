#!/usr/bin/env python3
'''
Load the API configs from the dot env files
'''

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"

# All the main imports
import os
import yaml
import argparse

tui_mode = False  # Variable that determines if the script runs in Text UI mode or just plain script mode
verbose = False   # Enabling or disabling it toggle verbose output of data mapping from this file

output_msg_buff = []
output_msg = ""
old_msg = ""


# The config file to be used when not passed as an argument, sits in the same directory of the app.py
default_config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.yaml'

arg_parser = argparse.ArgumentParser(description='Start the script in \'pure command line mode\' or in \'TUI mode\'')
arg_parser.add_argument("-c", "--config",
                        type=argparse.FileType('r', encoding='utf-8'),
                        help="path for the config file",
                        default=default_config_file,
                        required=False,
                        metavar=''
                        )
arg_parser.add_argument("-s", "--script",
                        help="launch in script mode",
                        action="store_true",
                        default=True)
arg_parser.add_argument("-u", "--tui",
                        help="launch in text ui mode",
                        action="store_true")
arg_parser.add_argument("-m", "--showmap",
                        help="during launch, first show the logical mapping of data between MQTT & SOCKETIO",
                        action="store_true")
arg_parser.add_argument("-a", "--auto",
                        help="doesn't ask for prompt for launching the script",
                        action="store_true")
args = arg_parser.parse_args()

if args.tui:
    tui_mode = True
    args.script = False
else:
    tui_mode = False
if args.showmap:
    verbose = True

# --- Loading data from config --- #
from dotenv import load_dotenv
# Loads mqtt credentials if any
load_dotenv()

# -- The config file itself, from cmd-line arguments or default -- #
conf_file = args.config.name
print('\n' + 'USED CONFIG FILE: ' + conf_file + '\n')
try:
    file_stream = open(conf_file, 'r')
except IOError:
    file_stream = None
    print("Note: config file doesn't exists")
    print('Make sure you have defined the \'config.yaml\'!')
    exit(0)

configs = yaml.safe_load(file_stream)

# Assign the comm network connect creds for protopie connect and mqtt
PROTO_PIE_CONNECT_HOST = configs['protopie_host']
PROTO_PIE_CONNECT_PORT = configs['protopie_port']

BRIDGE_NAME = configs['bridge_name']
MQTT_SECURED = configs['mqtt_secured']
MQTT_USR_NAME = None
MQTT_PWD = None
if MQTT_SECURED:
    MQTT_USR_NAME = os.getenv('MQTT_USR_NAME')
    MQTT_PWD = os.getenv('MQTT_PWD')

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
subs_payloads_list = []
emmission_msgids_list = []
emmission_values_list = []

for topic_to_msgid in TOPICS_TO_MSGIDS_LIST:
    # Extact subscription topics
    subs_topics_list.append(topic_to_msgid[0])
    # Extract socketio messageIDs
    emmission_msgids_list.append(topic_to_msgid[1])
for payload_to_value in PAYLOADS_TO_VALUES_LIST:
    # Extact payloads, respective to subscription topics
    subs_payloads_list.append(payload_to_value[0])
    # Extact values, that will replace the respective payloads
    emmission_values_list.append(payload_to_value[1])

# Check lengths to ensure data pattern
if (len(subs_topics_list) == len(subs_payloads_list) or len(emmission_msgids_list) == len(emmission_values_list)):
    if verbose:
        print('Mapping for MQTT -> socketio:')
        print('-----------------------------')
        for i in range(len(subs_topics_list)):
            print('For MQTT TOPIC:\'' + subs_topics_list[i] + '\' and PAYLOAD:\'' + subs_payloads_list[i] +
                  '\', the respective socketio translation is, MESSAGE_ID:\'' + emmission_msgids_list[i] +
                  '\' VALUE:\'' + emmission_values_list[i] + '\'')
        print('')
else:
    print('Patterns in [socketio->mqtt -> socketio] don\'t match!')
    print('Check the config file!')
    exit(0)


'''
For npycurses TUI, we want to visualzie the incoming mqtt messages,
mapped to as the outgoing protopie connect's socketio messages.
Thus mapping's arrangement
'''
subs_mqtt_msgs_list = []
emmission_sio_msgs_list = []

for i in range(0, len(subs_topics_list)):
    pl = ''
    if subs_payloads_list[i] == 'raw_payload':
        pl = '\'' + subs_payloads_list[i].upper() + '\''
    else:
        pl = subs_payloads_list[i]
    subs_mqtt_msgs_list.append(subs_topics_list[i] + ':' + pl)

for i in range(0, len(emmission_msgids_list)):
    msg = ''
    if emmission_values_list[i] == 'raw_value':
        msg = '\'' + emmission_values_list[i].upper() + '\''
    else:
        msg = emmission_values_list[i]
    emmission_sio_msgs_list.append(emmission_msgids_list[i] + ':' + msg)


# --- SOCKETIO -> MQTT --- #
subs_msgids_list = []
subs_values_list = []
pub_topics_list = []
pub_payloads_list = []

for msgid_to_topic in MSGIDS_TO_TOPICS_LIST:
    # Extact subscription saocketio messageIds (actually socketio doesn't need subscriptions.
    # It's just for the same mqtt type mental model)
    subs_msgids_list.append(msgid_to_topic[0])
    # Extract corresponding mqtt topics
    pub_topics_list.append(msgid_to_topic[1])
for value_to_payload in VALUES_TO_PAYLOADS_LIST:
    # Extact socketio values
    subs_values_list.append(value_to_payload[0])
    # Extract corresponding mqtt payloads (that are intended to replace the values)
    pub_payloads_list.append(value_to_payload[1])

# Check lengths to ensure data pattern
if len(subs_msgids_list) == len(subs_values_list) or len(pub_topics_list) == len(pub_payloads_list):
    if verbose:
        print('Mapping for socketio -> MQTT:')
        print('-----------------------------')
        for i in range(len(subs_msgids_list)):
            print('For socketio MESSAGE_ID:\'' + subs_msgids_list[i] + '\' and VALUE:\'' + subs_values_list[i] +
                  '\', the respective MQTT translation is, TOPIC:\'' + pub_topics_list[i] + '\' PAYLOAD:\'' +
                  pub_payloads_list[i] + '\'')
        print('')
else:
    print('Patterns in [socketio -> mqtt] don\'t match!')
    print('Check the config file!')
    exit(0)

'''
For npycurses TUI, we want to visualzie the data mapping
between incoming protopie connect socket io messages to
outgoing mqtt messages.
Thus mapping's arrangement
'''
subs_sio_msgs_list = []
pubs_mqtt_msgs_list = []
for i in range(0, len(subs_msgids_list)):
    msg_val = ''
    if subs_values_list[i] == 'raw_value':
        msg_val = '\'' + subs_values_list[i].upper() + '\''
    else:
        msg_val = subs_values_list[i]
    subs_sio_msgs_list.append(subs_msgids_list[i] + ':' + msg_val)
for i in range(0, len(pub_topics_list)):
    payload_val = ''
    if pub_payloads_list[i] == 'raw_payload':
        payload_val = '\'' + pub_payloads_list[i].upper() + '\''
    else:
        payload_val = pub_payloads_list[i]
    pubs_mqtt_msgs_list.append(pub_topics_list[i] + ':' + payload_val)


#  --- Ask before moving forward --- #
def ask_user_if_to_proceed(_question):
    while True:
        proceed = str(input(_question + ' [y/N]:')).lower().strip()
        if proceed[:1] == 'y':
            print('\nProceeding ...')
            break
        elif proceed == 'n':
            # don't proceed but exit
            print('\nExiting ...')
            print('\n')
            exit(0)
        else:
            print('\nInvalid input.\nPlease try again with \'y/Y\' or \'n/N\'\n')


if tui_mode:
    print('-----------------------------------------------------')
    print('Going to launch in \'Text User Interface\' [TUI] Mode')
    print('-----------------------------------------------------')
else:
    print('---------------------------------------------')
    print('Going to launch in regular simple script Mode')
    print('---------------------------------------------')


if verbose and not args.auto:
    '''
    If we have displayed in command line the data mapping,
    we should give people some time to read that and then
    ask them to propmt the proceeding
    '''
    ask_user_if_to_proceed('\nDo you want to Proceed')

if not verbose and not args.auto:
    '''
    If teh user didn't enable to see the data mapping and
    didn't pass in teh argument to auto proceed, prompt the user
    for proceeding
    '''
    ask_user_if_to_proceed('\nDo you want to Proceed')
