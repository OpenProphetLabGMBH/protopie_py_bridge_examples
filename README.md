# protopie_py_bridge_examples
A collection of bridge apps (written in python) that bridges between some typically used communication APIs like MQTT, OSC, Serial, MIDI, etc. to SocketIO, specific to [ProtoPieConnect](https://www.protopie.io/learn/docs/connect/getting-started) and [more details](https://protopie.notion.site/ProtoPie-Connect-Basics-Best-Practices-b68fec1986e9429ca71cc41e3905f095). 

## Why?


## Preparation & Installation:
1. Make sure you are using python3. 
2. [Install virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) to your specific system (if you haven't already)
    
    Every folder contains a virtual environment that I have created while developing the bridge apps, with a nomenclature of the env name as py_pie_API_bridge. 
3. Clone the repo: 
   ```shell
   git clone https://github.com/OpenProphetLabGMBH/protopie_py_bridge_examples.git
   ``` 
4. Each directory is dedicated to a separate _API_Protopie_bridge_. After cloning, enter your specific directory of interest.
5. Activate the virtual env in that dir, according to your shell environment: 
   ```shell
   # For bash
   source py_pie_<API_NAME>_bridge/bin/activate 
   # For fish
   source py_pie_<API_NAME>_bridge/bin/activate.fish 
   # etc. 
   ```
6. Once the virtual env is up and running, install the libraries:
   ```shell
   python3 -m pip install -r requirements.txt
   ```
7. Now your system and the virtaul env should be ready to test the api specific bridge apps: 
   ```shell
   python3 app.py
   ```

