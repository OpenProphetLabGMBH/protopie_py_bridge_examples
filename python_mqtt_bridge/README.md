# README

## Why is there a config file?

Explanation TBD

## TODO:

- [x] Modularize the whole script set.
- [ ] Format modules to be tested by itself (like `if name == __main__` for main app) 
- [x] Lint. 
- [x] Generalize `mqtt -> socketio` translation layer's business logic through a config file.
- [x] Generalize `socketio -> mqtt` translation layer's business logic through a config file.
- [ ] If similar mqtt topics in config file, subscribe only once. 
- [ ] Apply some arg-parse helpers
- [ ] Apply a npyscreen based TUI
- [ ] Give user to choose between script mode and TUI mode (using argparse)
- [ ] Create tests
