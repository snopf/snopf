#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)


"""
This is the python command line tool to control the usb device.

It can be run in interactive mode to select which action to perfom
- password requests
- send arbitrary messages
- set the devices secret
- change the keyboard delay for the device

If it is not run in interactive mode the string from the command line
will be used as the password request string and a password request will
be made.
"""

import usb_comm
import requests
import mnemonic
from password_generator import generate_password
from get_vers_info import get_commit

import sys
import os
import argparse
import textwrap
import ast
import cmd
import time

description = textwrap.dedent("""\
    This is the command line tool to request a password from
    the device. The tool can be used in interactive mode for multiple requests
    or once by parsing command line arguments. In interactive mode the
    device's secret can be set.
    """)

parser = argparse.ArgumentParser(
    description=description,
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('-i', '--interactive', 
                    help=('Start the tool in interactive mode.'),
                    action='store_true')

parser.add_argument('-e', '--hit_enter', 
                    help=('Instruct the device to automatically hit enter'
                        + ' after typing in the password.'),
                    action='store_true')
                    
parser.add_argument('-l', '--pw_length', 
                    help=('Length of the requested password in characters. '
                        + 'Must be between 6 and 40. Use pw_length=XX in '
                        + 'interactive mode to change the current password '
                        + 'length.'),
                    type=int, default=40)
                                                          
parser.add_argument('-s', '--string',
                    help=('Request string for the device. Multiple strings '
                        + 'will be concatenated to one message. To create a '
                        + 'Pin+Domain+Username message you can give three '
                        + 'string arguments in the order pin, domain, username '
                        + 'or one message with pin, domain username as one '
                        + 'string.'),
                    type=str, nargs='+')
                    
parser.add_argument('-v', '--version', help=('Version info'),
                    action='store_true')

args = parser.parse_args()


def send_message(msg_list, pw_length, hit_enter):
    if msg_list is None:
        msg = ''
    else:
        msg = ''.join(msg_list)
        
    try:
        msg = requests.reduce_message(msg)
        usb_comm.send_standard_pw_request(msg, pw_length,
                                          hit_enter=hit_enter)
        print('Sent message %s to the device.' % msg)
        print('Requested password length is %d.' % pw_length)

    except usb_comm.DeviceNotFound:
        print('Error: Could not find the USB device.')
        sys.exit(1)
        
        
class ArgError(Exception):
    pass

class Prompt(cmd.Cmd):
    
    def preloop(self):
        self.pw_length = 40
        self.hit_enter = False
    
    def emptyline(self):
        pass
    
    def do_pw_length(self, args):
        """
        Sets the password length to first argument. If no arguments
        are given, the current password length is shown."""
        if len(args) < 1:
            print('Current password length: %d' % self.pw_length)
            return
        
        try:
            pw_length = int(args)
            if not (6 <= pw_length <= 40):
                raise ValueError()
            self.pw_length = pw_length
            print('New password length: %d' % self.pw_length)
        except ValueError:
            print('Argument must be integer between 6 and 40. Password '
                + 'length not changed.')
    
    def do_hit_enter(self, args):
        """
        Add the 'hit enter' command to every password request.
        Can be set to either True or False. Without arguments the current
        value is shown.
        """
        if len(args) < 1:
            print('Current setting for hitting Enter is ' + str(self.hit_enter))
            return
        
        if not args in ['True', 'False']:
            print('Argument must be either \'True\' or \'False\'')
            return            

        self.hit_enter = bool(ast.literal_eval(args))
        print('New setting for hitting Enter is ' + str(self.hit_enter))
            
    def do_request(self, args):
        """
        Request a password from the device using the given string argument(s)
        and the set values for hit_enter and password length. Multiple strings
        will be concatenated to one.
        """
        send_message(args.split(), self.pw_length, self.hit_enter)
        
    def int_str_to_secret(self, data):
        """
        Convert the given string, representing a 128 bit integer, into a
        bytes instance of length 16
        """
        try:
            data = int(data)
        except ValueError:
            try:
                data = int(data, 16)
            except ValueError:
                print('Could not read integer value.')
                print('Must be either in base10 or base16.')
                raise ArgError()
        
        try:
            return data.to_bytes(16, sys.byteorder)
        except OverflowError:
            print('Entropy needs to be a 128 bit integer.')
            raise ArgError()
        
    def to_mnemonic(self, entropy):
        """Check sanity of args and return a 12 word mnemonic"""
        if not isinstance(entropy, bytes):
            entropy = self.int_str_to_secret(entropy)
        
        assert len(entropy) == 16
        
        m = mnemonic.to_mnemonic(entropy)
        print('***************************************************************')
        print('The resulting 12 word mnemonic for your input is:')
        print(' '.join(m))
        print('***************************************************************')
        return m

    def do_to_mnemonic(self, args):
        """
        Create a 12 word mnemonic from a 128 bit integer.
        The integer has to be in either decimal or hex notation.
        """
        args = args.split()
        if len(args) > 1 or len(args) == 0:
            print('Expected a single integer, got %d arguments.' % len(args))
            return
        try:
            self.to_mnemonic(args[0])
        except ArgError:
            pass
        
    def do_change_secret(self, args):
        """
        Change the secret on the device. WARNING Be sure that you know what
        you are doing!
        The argument for this command can be either 
            * A 12 word mnemonic following BIP39 or
            * A 128 bit integer in decimal or hex notation
        If no argument is given, a new secret is created from the systems
        randomness source.
        """
        args = args.split()
        if len(args) > 1:
            m = args
            # We assume a 12 word mnemonic
            if len(m) < 12:
                print(
                    'Error: Expected a 12 word mnemonic, got %d words instead.'
                    % len(m))
                return
            
            wordlist = mnemonic.read_word_list()
            
            for word in m:
                if not word in wordlist:
                    print('Error: Word %s not in wordlist.' % word)
                    return
                
            secret = mnemonic.to_entropy(m)
                    
        elif len(args) == 1:
            # We assume a 128 bit integer
            try:
                secret = self.int_str_to_secret(args[0])
                m = self.to_mnemonic(secret)
            except ArgError:
                pass
            
        else:
            print('No secret given, new secret will be created from system.\n')
            secret = os.urandom(16)
            m = self.to_mnemonic(secret)
            
        # Let's be sure nothing went wrong with all the fancy conversion
        # routines
        assert m == mnemonic.to_mnemonic(secret)
        assert secret == mnemonic.to_entropy(m)
        
        # Start of the actual secret change
        print('\n\nStarting the secret update.')
        print('Do not leave this window until the secret update is complete.\n\n')
        print('Sent new secret to the device. (The red lamp should be blinking.)')
        print('Press the Button for five consecutive seconds to continue with'
            + 'the secret update.')
        print('The device will type \'ready\' into the console if everything'
            + 'is ok.')
        print('DO NOT PRESS ANY KEY ON YOUR KEYBOARD.')
        
        try:
            usb_comm.send_new_secret(secret)
        except usb_comm.DeviceNotFound:
            print('\nError: USB device not connected.')
            return
        
        inp = input()
        
        if inp != 'ready':
            print ('Device did not sent \'ready\'. Aborting secret update.')
            usb_comm.send_shutdown_message()
            return
               
        print('Got \'ready\' message.')
        print('\nTesting the device with a random password request.')
        print('DO NOT PRESS ANY KEY ON YOUR KEYBOARD.')
        print('Press the Button on the device when the red led is on.')
        
        # We'll add a little delay so that the user can remove their finger
        # from the button
        time.sleep(.5)
        
        random_request = requests.reduce_message(os.urandom(50))
        
        usb_comm.send_standard_pw_request(random_request, 40, hit_enter=True)
        
        inp = input('Response from device: ')
        
        pw = generate_password(secret, random_request)
        print('Expected response: ', pw)
        if not pw == inp:
            print('Something went wrong, the device sent the wrong password.')
            print('Device will keep old secret.')
            print('Aborting secret update.')
            usb_comm.send_shutdown_message()
            return
        
        print('Device sent the correct password.')
        print('The new secret on the device is now set!')
        usb_comm.send_empty_message()
                
    def do_set_keyboard_delay(self, args):
        """Set the delay between key presses for the device in milliseconds"""
        args = args.split()
        if len(args) < 1:
            print('Need one argument (delay time in ms as integer)')
            return
        try:
            ms = int(args[0])
        except ValueError:
            print('Argument needs to be integer.')
            return
        usb_comm.set_kb_delay(ms)
        print('Press the button on snopf within 10 seconds to set the delay'
            + ' to the new value.')
        
    def do_quit(self, args):
        """Leave the interactive mode"""
        sys.exit(0)
        
    def do_EOF(self, args):
        print('\n')
        self.do_quit(args)
        
    def do_clear(self, args):
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('cls')

if __name__ == '__main__':
    if args.version:
        print('Version info: ' + get_commit())
    elif args.interactive:
        prompt = Prompt()
        prompt.prompt = '> '
        prompt.cmdloop()
    else:
        if not (usb_comm.MIN_PW_LENGTH <= args.pw_length <= usb_comm.MAX_PW_LENGTH):
            parser.error('Given password length must be between 6 and 40.')
        send_message(args.string, args.pw_length, args.hit_enter)
