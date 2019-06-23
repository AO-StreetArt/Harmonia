# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2017 Alex Barry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: Alex Barry
"""

# Standard Python Libraries
import sys
import json
import logging

# MIDI Connectivity
import mido

# OS Event generation
import pyautogui

# Filter an input value
def filter_input(type, value, config_note):
    if 'value' in config_note:
        if config_note["value"] != value:
            return False
    if config_note["type"] != type:
        return False
    return True

# Generate an OS Event based on the configured option
def generate_os_event(config_note, value):
    logging.debug("Generating Event for configuration: %s", config_note)

    if config_note["action"]["type"] == "keyboard":
        # Generate a keyboard event with modifiers
        for key in config_note["action"]["modifiers"]:
            # Press down modifier keys
            pyautogui.keyDown(key)
        pyautogui.press(config_note["action"]["key"])
        for key in config_note["action"]["modifiers"]:
            # Release modifier keys
            pyautogui.keyUp(key)

# Set up the file logging config
def config_logging(log_level):
    FORMAT = '%(asctime)-15s %(message)s'
    if log_level == 'Debug':
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    elif log_level == 'Info':
        logging.basicConfig(format=FORMAT, level=logging.INFO)
    elif log_level == 'Warning':
        logging.basicConfig(format=FORMAT, level=logging.WARNING)
    elif log_level == 'Error':
        logging.basicConfig(format=FORMAT, level=logging.ERROR)
    else:
        print("Log level not set to one of the given options, defaulting to debug level")
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)

def execute_main(config_file):
    conf_json = None
    with open(config_file, 'r') as cfile:
        conf_json = json.load(cfile)

    config_logging(conf_json["log_level"])
    logging.info("Starting Midi Server")

    inp_list = mido.get_input_names()
    logging.debug(inp_list)

    # Find the correct input MIDI Port
    for name in inp_list:
        if name.find(conf_json["device"]["name"]) != -1:

            # Open up the input MIDI port
            logging.info('Using input Midi Port: %s', name)
            inport = mido.open_input(name)

            # Recieve inbound MIDI messages
            while True:
                msg = inport.receive()
                if msg.type != 'control_change':
                    logging.debug('Message Recieved, Type: %s, Note: %s, Velocity: %s', msg.type, msg.note, msg.velocity)

                    # Filter the message
                    if str(msg.note) in conf_json["device"]["notes"]:
                        config_note = conf_json["device"]["notes"][str(msg.note)]
                        if filter_input(msg.type, msg.velocity, config_note):
                            # Execute the configured action
                            generate_os_event(config_note, msg.velocity)

                else:
                    logging.debug('Control change recieved, Control ID: %s -- Value: %s', msg.control, msg.value)

                    # Filter the message
                    if str(msg.control) in conf_json["device"]["notes"]:
                        config_note = conf_json["device"]["notes"][str(msg.note)]
                        if filter_input(msg.type, msg.value, config_note):
                            # Execute the configured action
                            generate_os_event(config_note, msg.value)

            return 0

    return -1

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            sys.exit(execute_main(sys.argv[1]))
        except KeyboardInterrupt:
            print('Keyboard Interrupt Detected, Exiting')
            sys.exit(1)
    else:
        print('Incorrect Inputs')
