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
# import curses
# import npyscreen
# npyscreen.disableColor()

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
    # [2] Then satrt the socketio service
    sio_sys.start_client(PROTO_PIE_CONNECT_HOST, PROTO_PIE_CONNECT_PORT)

    # app = App()
    # app.run()

# # class App(npyscreen.NPSApp):
# #     def main(self):
# #         form = npyscreen.FormBaseNew(name="ANDROID CTRL DAEMON VIEW")

# #         widget_fb_stat = form.add(Column, name="FIRE-BASE DB", relx=2, rely=2 + 12, max_width=30, height=8)  
# #         while True:
# #             form.display()

# # class Column(npyscreen.BoxTitle):
# #     def resize(self):
# #         self.max_height = int(0.73 * terminal_dimensions()[0])

# # def terminal_dimensions():
# #     return curses.initscr().getmaxyx()

    # app = App()
    # app.run()

# class App(npyscreen.NPSApp):
#     def main(self):
#         form = npyscreen.FormBaseNew(name="ANDROID CTRL DAEMON VIEW")

#         widget_fb_stat = form.add(Column, name="FIRE-BASE DB", relx=2, rely=2 + 12, max_width=30, height=8)       
#         while True:
#             form.display()

# class Column(npyscreen.BoxTitle):
#     def resize(self):
#         self.max_height = int(0.73 * terminal_dimensions()[0])

# def terminal_dimensions():
#     return curses.initscr().getmaxyx()


if __name__ == '__main__':
    ''' This is executed when run from the command line '''
    try:
        main()
    except KeyboardInterrupt:
        mqtt_sys.stop_client()
        sio_sys.stop_client()
        exit(0)
