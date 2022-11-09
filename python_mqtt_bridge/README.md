# README

## Why is there a config file?

Explanation TBD

## TODO:

- [x] Modularize the whole script set.
- [x] Lint.
- [x] Generalize `mqtt -> socketio` translation layer's business logic through a config file.
- [x] Generalize `socketio -> mqtt` translation layer's business logic through a config file.
- [x] Handle unintended messages in sockeio client.
- [x] Clean exit method of `'ctrl-c'` (Solve: kill threads when exiting in a clean fashion.)
- [ ] If similar mqtt topics in config file, subscribe only once.
- [ ] Apply some arg-parse helpers.
- [ ] Apply a npyscreen based TUI.
- [ ] Give users choice between script mode and TUI mode (using argparse).
- [ ] Create tests.
