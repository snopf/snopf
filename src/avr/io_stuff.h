// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __io_stuff_h__
#define __io_stuff_h__

#include <avr/io.h>

// Some routines for using the Button / LED IO pin

// Only IO pin left
#define IO_BUTTON_PIN PB0

// Evaluates to 1 if button is pressed (set to GND)
#define IO_BUTTON_PRESSED (!(PINB & (1 << IO_BUTTON_PIN)))

// Activate the button
void io_bttn_activate(void);

// Deactivate the button
void io_bttn_deactivate(void);

// Wait the given number of seconds for the user to press the button
// Returns 1 if the user pressed the button, else 0
uint8_t io_wait_for_user_bttn(uint8_t num_sec);

// Shut down the device and just keep blinking the LED slowly
void io_failure_shutdown(void);

#endif
