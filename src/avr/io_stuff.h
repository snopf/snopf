// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __io_stuff_h__
#define __io_stuff_h__

#include <avr/io.h>

// Some macros and functions for reading the button status
// and setting the LED pin

// We use the reset pin PB5 as button input
#define IO_BUTTON_PIN PB5

// PB0 is the LED pin
#define IO_LED_PIN PB0

// Evaluates to 1 if button is pressed (set to GND)
#define IO_BUTTON_PRESSED (!(PINB & (1 << IO_BUTTON_PIN)))

// Switch LED on (setting output low)
#define IO_LED_ON (PORTB &= ~(1 << IO_LED_PIN))

// Switch LED off (setting output high)
#define IO_LED_OFF (PORTB |= (1 << IO_LED_PIN))

// Set LED pin as output, Button pin as input
void io_init(void);

// Wait the given number of seconds for the user to press the button
// Returns 1 if the user pressed the button, else 0
uint8_t io_wait_for_user_bttn(uint8_t num_sec);

// Shut down the device and just keep blinking the LED slowly
void io_failure_shutdown(void);

#endif
