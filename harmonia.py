# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 14:46:33 2017

@author: alex
"""

# Standard Python Libraries
import ConfigParser
import sys
import json
import logging

# MIDI Connectivity
import mido

# Redis Connectivity
kill_redis = False
try:
    import redis
except Exception as e:
    print('Redis Driver not found, killing redis connections')
    kill_redis = True

# Cache which abstracts Redis vs Dict
class Cache(object):
    
    def __init__(self, cache_type, host, port, db):
        self.ctype = cache_type
        self.chost = host
        self.cport = port
        self.cdb = db
        
        self.redis_connection = None
        self.internal_cache = None
        
        if self.ctype == 'redis':
            self.redis_connection = redis.StrictRedis(host=self.chost, port=self.cport, db=self.cdb)
        elif self.cytpe == 'dict':
            self.internal_cache = {}
        else:
            log.error('Unknown Cache Type')
        
    def set_value(self, key, val):
        if self.ctype == 'redis':
            self.redis_connection.set(key, val)
        elif self.cytpe == 'dict':
            self.internal_cache[key] = val
    
    def get_value(self, key):
        if self.ctype == 'redis':
            return self.redis_connection.get(key)
        elif self.cytpe == 'dict':
            return self.internal_cache[key]
    
    def exists(self, key):
        if self.ctype == 'redis':
            return self.redis_connection.exists(key)
        elif self.cytpe == 'dict':
            if key in self.internal_cache:
                return True
            else:
                return False

#Set up the file logging config
def config_logging(log_file, log_level):
    if log_level == 'Debug':
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
    elif log_level == 'Info':
        logging.basicConfig(filename=log_file, level=logging.INFO)
    elif log_level == 'Warning':
        logging.basicConfig(filename=log_file, level=logging.WARNING)
    elif log_level == 'Error':
        logging.basicConfig(filename=log_file, level=logging.ERROR)
    else:
        print("Log level not set to one of the given options, defaulting to debug level")
        logging.basicConfig(filename=log_file, level=logging.DEBUG)

def execute_main(config_file):
    
    global kill_redis
    
    # Read the configuration file
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    
    # Pull Configuration values from the ini file
    inp_midi_name = config.get('Connection', 'Input')
    out_midi_name = config.get('Connection', 'Output')
    redis_host = config.get('Redis', 'Host')
    redis_port = config.get('Redis', 'Port')
    redis_db = config.get('Redis', 'DB')
    note_mapping = config.get('Notes', 'NoteMap')
    log_file = config.get('Logging', 'File')
    log_level = config.get('Logging', 'Level')
    
    # Configure Logging
    config_logging(log_file, log_level)
    
    # Connect to Redis
    cache = None
    if kill_redis or ((redis_host is None or redis_host = "") and (redis_port is None or redis_port = "") and (redis_db is None or redis_db = "")):
        cache = Cache('dict', None, None, None)
    else:
        try:
            cache = Cache('redis', redis_host, redis_port, redis_db)
        except Exception as e:
            logging.error('Error connecting to Cache')
            logging.error(e)
            sys.exit(-1)

    # Parse the Note Map
    try:
        note_map = json.loads(note_mapping)
    except Exception as e:
        logging.error('Error parsing Note Map')
        logging.error(e)
        sys.exit(-1)
    note_list = note_map['Notes']
    for note in note_list:
        cache.set_value('%s-%s' % (note['Input']['Type'], note['Input']['Note']), '%s-%s' % (note['Output']['Type'], note['Output']['Note']))
    
    inp_list = mido.get_input_names()
    logging.debug(inp_list)
    
    # Find the correct input MIDI Port
    for name in inp_list:
        if name.find(inp_midi_name) != -1:
    
            # Open up the input MIDI port
            logging.info('Using input Midi Port: %s' % name)
            inport = mido.open_input(name)
            
            # Recieve inbound MIDI messages
            while True:
                msg = inport.receive()
                if msg.type != 'control_change':
                    logging.info('Message Recieved, Type: %s, Note: %s, Velocity: %s' % (msg.type, msg.note, msg.velocity))
                    inp_type = msg.type
                    inp_note = msg.note
                    # Check if the message type & note exist in Redis
                    if cache.exists('%s-%s' % (inp_type, inp_note)):
                        
                        # Pull the new type and note out of redis
                        new_msg_attr = cache.get_value('%s-%s' % (inp_type, inp_note))
                        logging.debug('Object found in Cache: %s' % new_msg_attr)                        
                        dash_pos = new_msg_attr.rfind('-')
                        new_msg_type = new_msg_attr[0:dash_pos-1]
                        new_msg_note = new_msg_attr[dash_pos+1:len(new_msg_attr)]
                        
                        # Update the message based on the values returned from redis
                        msg.type = new_msg_type
                        msg.note = new_msg_note
                        
                    # Send the outbound message
                    
                    # Get a list of output ports
                    out_list = mido.get_output_names()
                    logging.debug(out_list)
                    
                    # Find the first loop MIDI port 
                    for out_name in out_list:
                        if out_name.find(out_midi_name) != -1:
                            outport = mido.open_output(out_name)
                            outport.send(msg)
                            logging.debug('Message sent on port %s' % out_name)
            else:
                logging.debug('Control change recieved')
                
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