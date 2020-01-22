// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "io_stuff.h"
#include "poll_delay.h"
#include <avr/interrupt.h>
#include <util/delay.h>

void io_bttn_activate(void)
{
    // Deactivate internal pullup
    PORTB &= ~(1 << IO_BUTTON_PIN);
    // Set the Button pin as input
    DDRB &= ~(1 << IO_BUTTON_PIN);
}

void io_bttn_deactivate(void)
{
    // Set the Button pin as output
    DDRB |= (1 << IO_BUTTON_PIN);
    // Set to GND to deactivate LED
    PORTB &= ~(1 << IO_BUTTON_PIN);
}

uint8_t io_wait_for_user_bttn(uint8_t num_sec)
{
    io_bttn_activate();
    
    for (uint8_t i = 0; i < num_sec * 10; i++) {
        poll_delay_ms(100);
        if (IO_BUTTON_PRESSED) {
            io_bttn_deactivate();
            return 1;
        }
    }
    // The user didn't press the button in time
    io_bttn_deactivate();
    return 0;
}

void io_failure_shutdown(void)
{
    cli();
    while (1) {
        // led on
        io_bttn_deactivate();
        PORTB |= (1 << IO_BUTTON_PIN);
        _delay_ms(500);
        // led off
        PORTB &= ~(1 << IO_BUTTON_PIN);
        _delay_ms(500);
    }
}
