# Harmonia

Harmonia is a Python application which can transform MIDI notes into native
keyboard events.

This project was born from my frustration at my inability to use my MIDI
equipment to control most programs that I use on a daily basis.  Now, your
MIDI equipment can control anything, without needing to rely on in-application
integrations.

## Configuration

Harmonia is largely reliant on it's configuration file to function correctly.

## Dependencies

For Linux users:

    pip install --user python-rtmidi mido python3-xlib pillow pyautogui

For OSX users:

    pip install python-rtmidi mido pyobjc-core pyobjc pyautogui

For Windows users:

    pip.exe install python-rtmidi mido pyautogui
