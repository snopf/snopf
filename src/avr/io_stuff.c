// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "io_stuff.h"
#include "poll_delay.h"
#include <avr/interrupt.h>
#include <util/delay.h>

void io_init(void)
{
    // Set the Button pin as input
    DDRB &= ~(1 << IO_BUTTON_PIN);
    // Set the LED pin as output
    DDRB |= (1 << IO_LED_PIN);
    
    IO_LED_OFF;
}

uint8_t io_wait_for_user_bttn(uint8_t num_sec)
{
    IO_LED_ON;
    
    for (uint8_t i = 0; i < num_sec * 10; i++) {
        poll_delay_ms(100);
        if (IO_BUTTON_PRESSED) {
            IO_LED_OFF;
            return 1;
        }
    }
    // The user didn't press the button in time
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
