# Harmonia

Harmonia is a Python service which can transform MIDI notes en-route.

## Dependencies

    pip install mido

    pip install redis (optional)

## Use

Harmonia requires a configuration file in order to execute.  Here's the example:

    [Logging]
    File: harmonia.log
    Level: Debug

    [Connection]
    Input: loopMIDI
    Output: loopMIDI

    [Redis]
    Host: localhost
    Port: 6379
    DB: 0

    [Notes]
    NoteMap: {Notes:  [
                        {
                          Input: {Type: 'note_on', Note: 60},
                          Output: {Type: 'note_off', Note: 60}
                        },
                        {
                          Input: {Type: 'note_off', Note: 60}, 
                          Output: {Type: 'note_on', Note: 60}
                        }
                      ]
                    }

The entries in the Logging section control Harmonia's logging.

The entries in the Connection section determine what MIDI connection Harmonia recieves from & sends to.

The entries in the Redis section can be populated to use a Redis server for persistence, or left blank to have an in-memory cache.

The Notes section should contain a NoteMap which is in JSON format.  See the format above, which shows an example of the off/on notes being switched.

