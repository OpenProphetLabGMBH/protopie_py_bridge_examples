# python3 based ProtoPieConnect bridge apps
A collection of bridge apps (written in python) that bridges between some typically used communication APIs like MQTT, OSC, Serial, MIDI, etc. to SocketIO, specific to [ProtoPieConnect](https://www.protopie.io/learn/docs/connect/getting-started) ([more details](https://protopie.notion.site/ProtoPie-Connect-Basics-Best-Practices-b68fec1986e9429ca71cc41e3905f095)). 

## Why?
One might come across a situation where they might have to test their prototypes, developed using ProtoPie, with other HW or SW systems. As an example, let's think of a situation where you might have an IoT dashboard designed and you want to test it against some real data, affecting the dashboard items and vice versa, for demo purposes or user testing, what ever it may be. In such a situation, or other similar situations, one would typically have to develop quickly a frontend app (using some JS frameworks or native app dev solutions), based on the UI design, which then can talk to the IoT protocol (let's say the IoT HW is talking in MQTT, for example). Now what if you don't have that frontend developer handy or it's time consuming to develop such an app. Wouldn't it be nice, if your ProtopPie demo app can talk to the hardware or vice versa. 

Now, if our HW device(or other SW system), is talking one of the API from the list, you can deploy one of these bridge apps. 
![system diagram](/assets/system_diagram/system_diagram.001.png "System Diagram")

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

