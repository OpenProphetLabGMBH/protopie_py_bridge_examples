# protopie_py_bridge_examples

## Preparation & Installation:
1. Make sure you are using python3. 
2. [Install virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) to your specific system (if you haven't already)
    
    Every folder contains a virtual environment that I have created while developing the bridge apps, with a nomenclature of the env name as py_pie_API_bridge. 
3. Clone the repo: 
   ```shell
   git clone https://github.com/OpenProphetLabGMBH/protopie_py_bridge_examples.git
   ``` 
4. After cloning, enter your specific directory of interest.
5. Activate the venv in that dir, accoridng to your shell environment: 
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
7. Now your system and the virtaul env shoudl be ready to test the api specific bridge apps: 
   ```shell
   python3 app.py
   ```

