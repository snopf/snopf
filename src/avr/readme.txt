The main loop simply calls usbPoll regularly and checks the number of received
bytes from the host. If the number of received bytes are matching the defined
length of our messages (18 bytes) the message will first be checked for a 
possible attempt to change the secret on the device. After a second check for
an attempt to change the delay between keypresses, the message will be treated
as a normal "type in a password" request. For that, the 128 bit long secret 
stored in the devices EEPROM will be concatenated with the last 16 bytes 
(128 bit) of the received message and the resulting SHA256 hash will be typed
into the host machine after a transformation into the Z85 base.

================================================================================
Modules overview:

io_stuff
    Activation of the button pin and a failure mode routine.
    
poll_delay
    Simple _delay_ms loops that call usbPoll regularly.
    
pw_generator
    Calls the SHA256 module and the Z85 module to generate the password.

secret
    Definition of the secret array in EEPROM and the routine to change the
    devices secret.
    
usb_comm
    Management of the buffer for received USB messages and processing of the
    HID specific requests by the host. The global message buffer is defined
    here and used by all other modules, that interpret the USB message.
    
usb_keyboard
    Some routines that translate ASCII codes to HID keycodes and type them
    into the host machine.
    
usbconfig
    Configuration for the usb driver.
    
sha256
    Implementation of SHA256 for the specific case (a 128 bit secret stored
    in the AVR EEPROM and a 128 bit message from the host machine).
    
z85
    Implementation of the Z85 base transformation optimized for the AVR.
