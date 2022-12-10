#!/usr/bin/env python3
'''
python app to redirect MQTT messages to Protopie socket messages and vice-versa
'''

__author__ = "Saurabh Datta"
__version__ = "0.1.0"
__license__ = "APACHE 2.0"

# --- FEW MAIN LIB IMPORTS -- #
import curses
import npyscreen
import threading


# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# -- LOCAL MODULE IMPORTS -- #
from preload import PROTO_PIE_CONNECT_HOST
from preload import PROTO_PIE_CONNECT_PORT
from preload import MQTT_BROKER_HOST
from preload import MQTT_BROKER_PORT
from preload import MQTT_SECURED
from preload import tui_mode
from preload import subs_mqtt_msgs_list
from preload import emmission_sio_msgs_list
from preload import subs_sio_msgs_list
from preload import pubs_mqtt_msgs_list
# import preload
import preload as pl

# --- FEW REM LIB IMPORTS -- #
import socket_io_handler as sio_sys
import mqtt_handler as mqtt_sys
import time


# npyscreen.disableColor()
# npyscreen.setTheme(npyscreen.Themes.ElegantTheme)
# print(npyscreen.Themes.ElegantTheme.default_colors)

def terminal_dimensions():
    return curses.initscr().getmaxyx()

class Column(npyscreen.BoxTitle):
    def resize(self):
        self.max_height = int(0.73 * terminal_dimensions()[0])

class BufferPagerBox(npyscreen.BoxTitle):
    '''Object for the widget that will show realtime info of processes and alerts'''
    _contained_widget = npyscreen.BufferPager

    def clear_buffer(self):
        '''Clear's the iwdget's buffer, if needed'''
        return self.entry_widget.clear_buffer()

    def buffer(self, *args, **values):
        '''widget's buffer to be filled by realtime data'''
        return self.entry_widget.buffer(*args, **values)

class App(npyscreen.NPSApp):
    '''Main App class holding all the widget windows'''
    def main(self):
        # main app form
        term_dims = curses.initscr().getmaxyx()
        height = int(term_dims[0])
        width = int(term_dims[1])

        form = npyscreen.FormBaseNew(name="MQTT<=>PROTOPIE-SOCKET-IO BRIDGE V:0.1")

        # mqtt stat board widget
        widget_mqtt_stat = form.add(
            Column,
            name="MQTT CONNECTION STATUS",
            relx=2, rely=2,
            max_width=40, height=5,
            color='LABEL')
        # socketio (for protopie) stat board widget
        widget_sio_stat = form.add(
            Column,
            name="PROTOPIE-CONNECT STATUS",
            relx=2 + 40, rely=2,
            max_width=40, height=5,
            color='LABEL')
        widget_desc = form.add(
            Column,
            name="DESCRIPTION",
            relx=2 + 40 + 40, rely=2,
            max_width=40, height=5,
            color='STANDOUT')
        input_mqtt_msg = form.add(
            Column,
            name="==> INPUT MQTT MSGS",
            relx=2, rely=2 + 5,
            max_width=40 * 2, height=len(subs_mqtt_msgs_list) + 2,
            color='CAUTIONHL')
        output_sio_msg = form.add(
            Column,
            name="OUTPUT PROTOPIE MSGS ==>",
            relx=2 + 40 * 2, rely=2 + 5,
            max_width=40, height=len(subs_mqtt_msgs_list) + 2,
            color='CURSOR_INVERSE')
        input_sio_msg = form.add(
            Column,
            name="INPUT PROTOPIE MSGS <==",
            relx=2 + 40 * 2, rely=2 + 5 + len(subs_mqtt_msgs_list) + 2,
            max_width=40, height=len(subs_sio_msgs_list) + 2,
            color='CAUTIONHL')
        output_mqtt_msg = form.add(
            Column,
            name="<== OUTPUT MQTT MSGs",
            relx=2, rely=2 + 5 + len(subs_mqtt_msgs_list) + 2,
            max_width=40 * 2, height=len(pubs_mqtt_msgs_list) + 2,
            color='CURSOR_INVERSE')
        std_out_panel = form.add(
            BufferPagerBox,
            name='PROCESS OUTPUT MONITOR',
            relx=2, rely=2 + 5 + len(subs_mqtt_msgs_list) + 2 + len(pubs_mqtt_msgs_list) + 2,
            height=25, max_width=40 * 3,
            editable=False,
            color='WARNING'
        )

        # watch the form and update values
        while True:
            widget_mqtt_stat.values = [
                "BROKER:    " + str(MQTT_BROKER_HOST) + ":" + str(MQTT_BROKER_PORT),
                "SECURED:   " + str(MQTT_SECURED),
                "CONNECTED: " + str(mqtt_sys.mqtt_client.is_connected())
            ]
            widget_sio_stat.values = [
                "SERVER:    " + str(PROTO_PIE_CONNECT_HOST) + ":" + str(PROTO_PIE_CONNECT_PORT),
                "SECURED:   " + "False [method TBD]",    # [TBD] For connect embedded, there may be a secure sol
                "CONNECTED: " + str(sio_sys.io.connected)
            ]
            widget_desc.values = [
                "CREATOR:  " + "Saurabh Datta",
                "LOCATION: " + "BER, DE",
                "YEAR:     " + "2022"
            ]
            input_mqtt_msg.values = subs_mqtt_msgs_list
            output_sio_msg.values = emmission_sio_msgs_list
            input_sio_msg.values = subs_sio_msgs_list
            output_mqtt_msg.values = pubs_mqtt_msgs_list

            if not mqtt_sys.mqtt_client.is_connected():
                widget_mqtt_stat.color = 'CRITICAL'
            else:
                widget_mqtt_stat.color = 'GOOD'
            if not sio_sys.io.connected:
                widget_sio_stat.color = 'CRITICAL'
            else:
                widget_sio_stat.color = 'GOOD'

            
            if len(pl.output_msg_buff) >= 1:
                std_out_panel.buffer(pl.output_msg_buff, scroll_end=True)
                pl.output_msg_buff = []

            form.display()



def pio_server_thread_func():
    sio_sys.start_client(PROTO_PIE_CONNECT_HOST, PROTO_PIE_CONNECT_PORT)

def main():
    ''' Main entry point of the app '''
    # [1] First start mqtt service
    mqtt_sys.start_client(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    # [2] Then start the socketio service ...
    # Note: Based on script mode or TUI mode, different spawing methods)
    if tui_mode:
        pio_server_thread = threading.Thread(target=pio_server_thread_func, )
        pio_server_thread.start()
    else:
        sio_sys.start_client(PROTO_PIE_CONNECT_HOST, PROTO_PIE_CONNECT_PORT) 
    # [3] Show TUI based on the set flag's state
    if tui_mode:
        app = App()
        app.run()




if __name__ == '__main__':
    ''' This is executed when run from the command line '''
    try:
        main()
    except KeyboardInterrupt:
        print('\nExiting ...')
        mqtt_sys.stop_client()
        sio_sys.stop_client()
        exit(0)
