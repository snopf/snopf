// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "io_stuff.h"
#include "poll_delay.h"
#include <avr/interrupt.h>
#include <util/delay.h>
#include "usbdrv.h"

void io_init(void)
{
    // Set the Button pin as input
    DDRB &= ~(1 << IO_BUTTON_PIN);
    // Set the LED pin as output
    DDRB |= (1 << IO_LED_PIN);
    
    IO_LED_OFF;
}

int8_t io_wait_for_user_bttn(void)
{
#ifdef AVR_TESTING_NO_USER_INPUT
    return 1;
#endif
    IO_LED_ON;
    
    // Wait 10 seconds for the user to press the button
    for (uint16_t i = 0; i < 2000; i++) {
        _delay_ms(5);
        if (IO_BUTTON_PRESSED) {
            IO_LED_OFF;
            return 1;
        }
        usbPoll();
    }
    // The user didn't press the button in time
    IO_LED_OFF;
    return 0;
}

int8_t io_wait_for_user_bttn_hold(void)
{
#ifdef AVR_TESTING_NO_USER_INPUT
    return 1;
#endif
    IO_LED_ON;
    uint8_t pressed = 0;
    for (uint8_t i = 0; i < 200; i++) {
        IO_LED_TOGGLE;
        poll_delay_ms(100);
        if (IO_BUTTON_PRESSED) {
            pressed++;
        } else {
            pressed = 0;
        }
        if (pressed >= 50) {
            IO_LED_OFF;
            return 1;
        }
    }
    IO_LED_OFF;
    return 0;
}

void io_failure_shutdown(void)
{
    cli();
    while (1) {
        IO_LED_ON;
        _delay_ms(500);
        IO_LED_OFF;
        _delay_ms(500);
    }
}
