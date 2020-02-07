#!/usr/bin/env python3 -u

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)


"""
Interface between the browser extension and
    a) the USB module and 
    b) the account table file
"""

import sys
sys.path.append('..')

import usb_comm
import requests
from get_vers_info import get_commit

import json
import logging
import os
import fcntl

app_path = os.getcwd()

# TODO write test script, at least for requests!

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='snopf_driver.log',
                    filemode='w')

def get_msg():
    """Read new message from extension"""
    msg_length = sys.stdin.buffer.read(4)
    if len(msg_length) == 0:
        logging.info("Received exit signal")
        sys.exit(0)
    msg_length = int.from_bytes(msg_length, sys.byteorder)
    msg = sys.stdin.buffer.read(msg_length)
    logging.info("Got message %s" % msg)
    data = json.loads(msg)
    return data['cmd'], data.get('msg', '')

def pack_data(cmd, msg):
    """Packs cmd + message to json"""
    return json.dumps({'cmd': cmd, 'msg': msg}).encode()

def get_length_int(data):
    """Get length of data as 4 byte int"""
    return (len(data)).to_bytes(4, sys.byteorder)

def send_msg(cmd, msg):
    """Send message to extension"""
    data = pack_data(cmd, msg)
    length = get_length_int(data)
    sys.stdout.buffer.write(length)
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    logging.info("Send message %s" % msg)
    
def error(err_msg):
    """Log error message err_msg and send it to extension"""
    logging.error(err_msg)
    send_msg('error', err_msg)
    
def load_account_table(account_table_path):
    try:
        with open(account_table_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        error('Password file not found')
        return {}
    
def insert_entry(entry, account_table):
    '''Insert entry in given account_table dict'''
    if not entry['hostname'] in account_table:
        account_table[entry['hostname']] = {}
        
    assert not entry['account'] in account_table[entry['hostname']]
    
    account_table[entry['hostname']][entry['account']] = {
        'password_length': entry['password_length'],
        'password_iteration': entry['password_iteration']
        }
        
def save_new_entry(entry, account_table_path):
    ''' Save new entry in account table file'''
    f = open(account_table_path, 'r+')
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return False
    # Get the current account table, other programs may have changed it
    account_table = load_account_table(account_table_path)
    insert_entry(entry, account_table)
    f.seek(0)
    json.dump(account_table, f)
    f.truncate()
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()
    return True

def entry_is_new(entry, account_table):
    return (not (entry['hostname'] in account_table)
            or not entry['account'] in account_table[entry['hostname']])
    
def main_loop():
    account_table_path = app_path + '/../snopf_manager/account_table.json'
    account_table = load_account_table(account_table_path)
    
    try:        
        while True:
            cmd, msg = get_msg()
            
            if cmd == 'get_account_table':
                send_msg(cmd, account_table)
                    
            elif cmd == 'check_device_available':
                send_msg(cmd, str(usb_comm.is_device_available()))
            
            elif cmd == 'request_password':
                msg['password_iteration'] = int(msg['password_iteration'])
                msg['password_length'] = int(msg['password_length'])
                if msg['save_new_info']:
                    if entry_is_new(msg, account_table):
                        if save_new_entry(msg, account_table_path):
                            account_table = load_account_table(
                                account_table_path)
                            send_msg('get_account_table', account_table)
                        else:
                            error('Cannot lock account table file')
                
                request = requests.combine_standard_request(msg)
                try:
                    usb_comm.send_standard_pw_request(
                        request, msg['password_length'],
                        hit_enter=msg['hit_enter'])
                except usb_comm.DeviceNotFound:
                    error('Device not connected')
            
            elif cmd == 'version':
                send_msg(cmd, get_commit())
                
            elif cmd == 'debug':
                logging.info(msg)
                
            else:
                error('Wrong message format')

    except Exception as e:
        logging.exception(str(e))

if __name__ == "__main__":
    logging.info("Application started")
    main_loop()
